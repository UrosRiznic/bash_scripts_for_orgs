#!/usr/bin/env python3

import os
import shutil

# Function made for logging.
# This function appends text (message) to the file called organize.log
def log_info(message):
    with open('organizer.log', 'a') as f:
        f.write(f"{message}\n")

# Function that does all the logic
# It takes 3 Arguments: Source of directory, Destination and action (move/copy)
# Checks if the targeted directory is a folder, if it is, it calls itself recursivly
# If it is file, i does all the logic
# Method on stripping the extension is simple, using the slices
# EXAMPLE: ("example.txt")[1]     -> .txt
# EXAMPLE: ("example.txt")[1][1:] ->  txt
def organize_files(src, dest, action):
    for item in os.listdir(src):
        item_path = os.path.join(src, item)
        if os.path.isdir(item_path):
            organize_files(item_path, dest, action)
        elif os.path.isfile(item_path):
            extension = os.path.splitext(item)[1][1:]
            dest_folder = os.path.join(dest, extension)
            dest_path = os.path.join(dest_folder, item)

            if item_path == dest_path:
                continue

            # Collision Handling part
            if os.path.exists(dest_path):
                print(f"File {dest_path} already exists. Overwrite/Skip/Rename? (o/s/r): ")
                choice = input().strip().lower()
                if choice == 's':
                    continue
                elif choice == 'r':
                    new_name = input("Enter new name: ")
                    dest_path = os.path.join(dest_folder, new_name)
                elif choice != 'o':
                    print("Invalid choice.")
                    return

            print(f"{action.capitalize()}ing: {item_path} -> {dest_path}")

            if action == 'move':
                shutil.move(item_path, dest_path)
            else:
                shutil.copy2(item_path, dest_path)

            log_info(f"{action} {item_path} -> {dest_path}")

# Function that removes Empty directories
def find_and_remove_empty_dirs(directory):
    empty_folders = []
    for dirpath, dirnames, filenames in os.walk(directory):
        if not dirnames and not filenames:
            empty_folders.append(dirpath)
            os.rmdir(dirpath)
            log_info(f"Removed empty folder: {dirpath}")

    return empty_folders

# Main function that calls everything
def main():
    # User puts location of the directorie, but make sure to handle to escape the location.
    source_dir = input("Enter the source directory: ").replace("\\", "/")
    source_dir = source_dir.replace(":", "")

    if not os.path.exists(source_dir):
        print("The directory does not exist.")
        return

    # User makes a choice of move/copy the files
    action = input("Do you want to move or copy files? (move/copy): ").strip().lower()

    if action not in ['move', 'copy']:
        print("Invalid option.")
        return

    # If user decides to copy, we make sure to make COPY_OF_THE_FOLDER to better organize the directory
    target_dir = source_dir
    if action == 'copy':
        target_dir = os.path.join(source_dir, "COPY_OF_THE_FOLDER")
        os.makedirs(target_dir, exist_ok=True)

    for root, dirs, files in os.walk(source_dir):
        for extension in {os.path.splitext(file)[1][1:] for file in files}:
            os.makedirs(os.path.join(target_dir, extension), exist_ok=True)

    organize_files(source_dir, target_dir, action)
    empty_folders = find_and_remove_empty_dirs(target_dir)

    if empty_folders:
        print("Empty folders removed:")
        for folder in empty_folders:
            print(folder)
    else:
        print("No empty folders found.")

    print("Task completed. Check organizer.log for details.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_info(f"An error occurred: {e}")
        print(f"An error occurred: {e}")
