#!/usr/bin/env python3

import os
import shutil
import sys
import magic
import timeit

# Function that moves files to a directory, based on they name
def classify_and_move(target_dir, filepath, mime):
    # file - similar to bash-script, var that stores file name (filepath)
    # is_exectutable just checks if the file is executable (chmod +x)
    file = os.path.basename(filepath)
    is_executable = os.access(filepath, os.X_OK)

    # rb - Read Binary. 
    # This is used for reading first line of the file, for checking shegang
    with open(filepath, 'rb') as f:
        first_line = f.readline().decode(errors='ignore').strip()

    # This code decides where eachf of the files will be caregorized, based on their mime type
    if is_executable or first_line.startswith("#!"):
        if not any(keyword in mime for keyword in ["video", "audio", "msword", "spreadsheet", "image"]):
            destination = "Programs"
        else:
            destination = "Other"
    elif "image" in mime:
        destination = "Images"
    elif "text" in mime or "pdf" in mime or "msword" in mime or "spreadsheet" in mime:
        destination = "Documents"
    elif "audio" in mime or "video" in mime:
        destination = "Video_and_Audio"
    elif not os.path.splitext(file)[1]:
        destination = "Files_without_extension"
    else:
        destination = "Other"

    # Code that creates folders based on the "destination" 
    # and in the same time moves the files
    destination_path = os.path.join(target_dir, destination)
    if not os.path.exists(destination_path):
        os.mkdir(destination_path)
    shutil.move(filepath, os.path.join(destination_path, file))
    print(f"Moved: {filepath} -> {destination_path}")

def remove_empty_dirs(root):
    for dirpath, _, _ in os.walk(root, topdown=False):
        if dirpath == root:
            continue
        if not os.listdir(dirpath):
            os.rmdir(dirpath)
            print(f"Deleted empty folder: {dirpath}")

def main(target_dir):
    if not os.path.isdir(target_dir):
        print("Error: Provided path is not a valid directory.")
        sys.exit(1)

    if not os.listdir(target_dir):
        print("The folder is empty.")
        sys.exit(0)

    # In this for loop, i used os.walk function, to go true every directory inside the folder
    # Here, the MIME type of the file is determined using the magic library. 
    # And lastly i call classify_and_move function to do exactly that.
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            filepath = os.path.join(root, file)
            mime = magic.Magic().from_file(filepath)
            classify_and_move(target_dir, filepath, mime)

    remove_empty_dirs(target_dir)
    print("Cleanup complete.")

def wrapper(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)
    return wrapped

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python python_automated_cleanup.py <path>")
        sys.exit(1)

    wrapped = wrapper(main, sys.argv[1])
    execution_time = timeit.timeit(wrapped, number=1)

    print(f"\nScript executed in {execution_time:.2f} seconds.")
