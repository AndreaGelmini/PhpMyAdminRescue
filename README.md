# PhpMyAdminRescue

## Description

This repository contains several Python scripts to manage the import of SQL dump files, the splitting of SQL files into smaller chunks, and the resolution of problems related to MySQL.

There is no real reason why I created these scripts. I had the need to find a way that didn't kill my pc when importing large data dump files into the local db. 

And above all to refresh my knowledge in Python.

### Requirements

Ensure you have Python 3.x installed. Additionally, some external libraries may be required. You can install them using the following command:

```bash
pip install pymysql
```

### Files and Commands

1. **importer.py**: This script imports data from a SQL dump file into a MySQL database. You can run the script with the following arguments:

   ```bash
   python importer.py --file <path_to_dump_file> --host <mysql_host> --user <mysql_user> --database <mysql_database_name> [--password <mysql_password>] [--port <mysql_port>] [--chunk-size <chunk_size>] [--error-log <error_log_file>]
   ```

2. **chunker.py**: This script splits a phpMyAdmin SQL file into smaller chunks. You can run the script with the following arguments:

   ```bash
   python chunker.py <file_input> <file_output> [--chunk-size <dimensione_chunk>] [--db-name <nome_database>]
   ```

3. **shutdown_unexpectedly_solver.py**: This script helps to solve problems related to MySQL unexpectedly shutting down. You can run the script simply with:

   ```bash
   python shutdown_unexpectedly_solver.py
   ```

### Note

- Ensure you have the necessary permissions to execute these scripts and access the specified files and folders.
- Check the generated logs for any errors during the execution of the scripts.

## Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/improvement`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature/improvement`)
6. Create a Pull Request

Please ensure your code follows the existing style and includes appropriate tests.

For major changes, please open an issue first to discuss what you would like to change.


## Donations

If you find this project useful, you can support my work with a donation:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/X8X415RASI)

