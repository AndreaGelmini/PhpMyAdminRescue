import argparse
import re
from typing import List, Optional

def split_phpmyadmin_insert(file_path: str, chunk_size: int = 1000, output_file: str = 'output.sql', db_name: Optional[str] = None):
    # Read the input file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract the table name
    table_match = re.search(r'INSERT INTO `(\w+)`', content)
    if not table_match:
        raise ValueError("Table name not found in the INSERT query")

    table_name = table_match.group(1)

    # Extract all values between parentheses
    values_pattern = r'\(((?:[^()]*|\([^()]*\))*)\)'
    values = re.findall(values_pattern, content)

    # Write the queries divided into chunks
    with open(output_file, 'w', encoding='utf-8') as out:
        if db_name:
            out.write(f"USE {db_name};\n\n")
        
        out.write(f"LOCK TABLES `{table_name}` WRITE;\n")
        out.write(f"/*!40000 ALTER TABLE `{table_name}` DISABLE KEYS */;\n")
        
        for i in range(0, len(values), chunk_size):
            chunk = values[i:i + chunk_size]
            # Generate the query for the current chunk
            values_string = ','.join('(' + v + ')' for v in chunk)
            insert_query = f"INSERT INTO `{table_name}` VALUES {values_string};\n"
            out.write(insert_query)
        
        out.write(f"/*!40000 ALTER TABLE `{table_name}` ENABLE KEYS */;\n")
        out.write("UNLOCK TABLES;\n")

def main():
    parser = argparse.ArgumentParser(description='Split a phpMyAdmin SQL file into chunks.')
    parser.add_argument('input_file', help='Path to the input file')
    parser.add_argument('output_file', help='Path to the output file')
    parser.add_argument('--chunk-size', type=int, default=5000, help='Chunk size (default: 5000)')
    parser.add_argument('--db-name', help='Database name to use')

    args = parser.parse_args()

    split_phpmyadmin_insert(args.input_file, args.chunk_size, args.output_file, args.db_name)

if __name__ == "__main__":
    main()