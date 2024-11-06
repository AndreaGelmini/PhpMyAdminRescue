import pymysql
import logging
import re
import sys
from datetime import datetime
import argparse

class DumpImporter:
    def __init__(self, host, user, database, password='', port=3306, error_log_file='error_queries.sql'):
        self.db_config = {
            'host': host,
            'user': user,
            'database': database,
            'port': port
        }

        if password:
            self.db_config['password'] = password
        self.error_log_file = error_log_file

        # Configure logging
        logging.basicConfig(
            filename='import_log.txt',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def connect(self):
        try:
            self.conn = pymysql.connect(**self.db_config)
            self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)  # Use the cursor for dictionary results
            logging.info("Database connection established")
        except pymysql.err.OperationalError as err:
            logging.error(f"Authentication error: {err}")
            print("Authentication error. Verify the database credentials.")
            sys.exit(1)
        except pymysql.err.InterfaceError as err:
            logging.error(f"Database connection error: {err}")
            print("Unable to connect to the database. Verify the connection parameters.")
            sys.exit(1)
        except pymysql.MySQLError as err:
            logging.error(f"Database connection error: {err}")
            print(f"Database connection error: {err}")
            sys.exit(1)
        except Exception as e:
            logging.error(f"Connection error or in `connect()`: {e}")
            print(f"Connection error or in `connect()`: {e}")
            sys.exit(1)

    def disconnect(self):
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conn'):
            self.conn.close()
        logging.info("Database connection closed")

    def extract_values_from_insert(self, insert_query):
        """Extract values from the INSERT query"""
        values_pattern = r'\(((?:[^()]*|\([^()]*\))*)\)'
        return re.findall(values_pattern, insert_query)

    def record_exists(self, table_name, primary_key_value):
        """Check if a record exists in the table"""
        try:
            query = f"SELECT 1 FROM {table_name} WHERE id = %s LIMIT 1"
            self.cursor.execute(query, (primary_key_value,))
            return self.cursor.fetchone() is not None
        except pymysql.MySQLError as err:
            logging.error(f"Error checking record: {err}")
            return False

    def log_error_query(self, query, error):
        """Log queries that generated errors"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.error_log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n-- Error at {timestamp}: {error}\n")
            f.write(f"{query};\n")

    def process_dump_file(self, file_path, chunk_size=1000):
        """Process the dump file"""
        try:
            self.connect()

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find the target table
            table_match = re.search(r'INSERT INTO `(\w+)`', content)
            if not table_match:
                raise ValueError("Table name not found in the INSERT query")

            table_name = table_match.group(1)
            values = self.extract_values_from_insert(content)

            processed_count = 0
            skipped_count = 0
            error_count = 0

            for value in values:
                try:
                    # Extract the ID from the value (assumes it's the first field)
                    id_match = re.match(r'(\d+)', value)
                    if not id_match:
                        continue

                    record_id = int(id_match.group(1))

                    # Skip if the record exists
                    if self.record_exists(table_name, record_id):
                        skipped_count += 1
                        logging.info(f"Record {record_id} already exists, skipped")
                        continue

                    # Build and execute the query for a single record
                    insert_query = f"INSERT INTO `{table_name}` VALUES ({value})"
                    self.cursor.execute(insert_query)
                    self.conn.commit()
                    processed_count += 1

                    if processed_count % 100 == 0:
                        logging.info(f"Processed {processed_count} records")

                except pymysql.MySQLError as err:
                    error_count += 1
                    logging.error(f"Error inserting record: {err}")
                    self.log_error_query(f"INSERT INTO `{table_name}` VALUES ({value})", err)
                    continue

            return {
                'processed': processed_count,
                'skipped': skipped_count,
                'errors': error_count
            }

        finally:
            self.disconnect()


def main():
    parser = argparse.ArgumentParser(description='Process a SQL dump and insert the data into the database')

    # Required arguments
    parser.add_argument('--file',
                       required=True,
                       help='Path to the SQL dump file')
    parser.add_argument('--host',
                       required=True,
                       help='MySQL database host')
    parser.add_argument('--user',
                       required=True,
                       help='MySQL database username')
    parser.add_argument('--database',
                       required=True,
                       help='MySQL database name')

    # Password made optional
    parser.add_argument('--password',
                       default='',
                       help='MySQL database password (optional)')

    # Port made optional
    parser.add_argument('--port',
                       type=int,
                       default=3306,
                       help='MySQL database port (default: 3306)')

    # Other optional arguments
    parser.add_argument('--chunk-size',
                       type=int,
                       default=1000,
                       help='Chunk size for processing (default: 1000)')
    parser.add_argument('--error-log',
                       default='error_queries.sql',
                       help='Log file for queries with errors (default: error_queries.sql)')

    args = parser.parse_args()

    # Create the processor instance with the provided parameters
    processor = DumpImporter(
        host=args.host,
        user=args.user,
        password=args.password,
        database=args.database,
        port=args.port,
        error_log_file=args.error_log
    )

    try:
        processor.connect()
        results = processor.process_dump_file(
            file_path=args.file,
            chunk_size=args.chunk_size
        )

        print(f"""
        Import completed:
        - Processed records: {results['processed']}
        - Skipped records (already exist): {results['skipped']}
        - Errors: {results['errors']}

        For more details, check the files:
        - Error log: {args.error_log}
        - Import log: import_log.txt
        """)

    except Exception as e:
        print(f"Error during processing: {e}")
        logging.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        processor.disconnect()

if __name__ == "__main__":
    main()