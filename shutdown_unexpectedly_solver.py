# Ispiration
# https://stackoverflow.com/questions/18022809/how-can-i-solve-error-mysql-shutdown-unexpectedly

import os
from datetime import datetime
import shutil
import subprocess

def is_mysql_running():
    """Verifica se MySQL di XAMPP è in esecuzione."""
    try:
        # Verifica il processo mysqld.exe
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq mysqld.exe"],
            capture_output=True,
            text=True
        )
        return "mysqld.exe" in result.stdout
            
    except subprocess.CalledProcessError as e:
        print(f"Errore durante la verifica dello stato di MySQL: {e}")
        return False

def stop_mysql():
    """Ferma il processo MySQL di XAMPP."""
    if is_mysql_running():
        try:
            subprocess.run(["taskkill", "/F", "/IM", "mysqld.exe"], check=True)
            print("MySQL è stato fermato con successo.")
        except subprocess.CalledProcessError as e:
            print(f"Errore durante l'arresto di MySQL: {e}")
    else:
        print("MySQL non è in esecuzione.")

def start_mysql():
    """Avvia MySQL di XAMPP."""
    try:
        # Assumi che mysqld.exe si trovi in questa posizione
        mysql_path = "C:\\xampp\\mysql\\bin\\mysqld.exe"
        subprocess.Popen([mysql_path, "--defaults-file=C:\\xampp\\mysql\\bin\\my.ini"])
        print("MySQL è stato avviato con successo.")
    except Exception as e:
        print(f"Errore durante l'avvio di MySQL: {e}")

# Rename folder mysql/data to mysql/data_old
def backUpOldFolder():
    now = datetime.now()
    formatted_time = now.strftime("%Y_%m_%d_%H_%M_%S")

    old_folder_name = "C:\\xampp\\mysql\\data"
    new_folder_name = f"C:\\xampp\\mysql\\bp_data_{formatted_time}"

    try:
        os.rename(old_folder_name, new_folder_name)
        print(f"BackUp of '{old_folder_name}' in '{new_folder_name}' succesofuly.")
    except FileNotFoundError:
        print(f"Error: folder '{old_folder_name}' not found.")
    except FileExistsError:
        print(f"Error: folder '{new_folder_name}' already exist.")
    except Exception as e:
        print(f"A Error occurent: {e}")

# Make a copy of mysql/backup folder and name it as mysql/data
def moveBackUpFolderToData():
    # Paths of the folders
    source_folder = "C:\\xampp\\mysql\\backup"  # Path of the source folder
    destination_folder = "C:\\xampp\\mysql\\data"  # Path of the destination folder

    if os.path.exists(destination_folder):
        print(f"Error: the folder '{destination_folder}' alredy exist.")
    else:
        try:
            shutil.copytree(source_folder, destination_folder)
            print(f"The folder '{source_folder}' succesofulid copied in '{destination_folder}'.")
        except Exception as e:
            print(f"An error occured: {e}")

# Copy all your database folders from mysql/data_old into mysql/data (except mysql, performance_schema, and phpmyadmin folders)
def moveOldsubFolder():
    # Paths of the folders
    source_folder = 'C:\\xampp\\mysql\\data_old'  # Path of the source folder
    destination_folder = 'C:\\xampp\\mysql\\data'  # Path of the destination folder

    # Folders to exclude
    excluded_folders = {'mysql', 'performance_schema', 'phpmyadmin'}

    # Check if the destination folder exists
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)  # Create the destination folder if it doesn't exist

    # Copy the folders from the source folder to the destination folder
    for folder_name in os.listdir(source_folder):
        # Check if the folder name is not in the excluded folders
        if folder_name not in excluded_folders:
            source_path = os.path.join(source_folder, folder_name)
            destination_path = os.path.join(destination_folder, folder_name)

            # Check if it's a folder
            if os.path.isdir(source_path):
                shutil.copytree(source_path, destination_path)
                print(f"Copied the folder '{folder_name}' from '{source_folder}' to '{destination_folder}'")
            else:
                print(f"'{folder_name}' is not a folder, so it's ignored.")

# Copy mysql/data_old/ibdata1 file into mysql/data folder
def moveOldFile():
    # Paths of the folders
    source_file = 'C:\\xampp\\mysql\\data_old\\ibdata1'  # Path of the source file
    destination_folder = 'C:\\xampp\\mysql\\data'          # Path of the destination folder
    destination_file = os.path.join(destination_folder, 'ibdata1')  # Path of the destination file

    # Check if the source file exists
    if os.path.exists(source_file):
        # Copy the file to the destination folder
        shutil.copy2(source_file, destination_file)
        print(f"File '{source_file}' copied in '{destination_file}' successfully.")
    else:
        print(f"Error: the file '{source_file}' doesn't exist.")


if __name__ == "__main__":
    try:
        # Stop MySQL service
        stop_mysql()  
        
        # Backup and restore data
        backUpOldFolder()
        moveBackUpFolderToData() 
        moveOldFile()

        # Restart MySQL service
        start_mysql()
        
        print("MySQL data recovery completed successfully")
        
    except Exception as e:
        print(f"An error occurred during recovery: {e}")
        print("Please check logs and try again")
