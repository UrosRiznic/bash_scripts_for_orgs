#!/usr/bin/env python3

import os
import sys
import shutil
import timeit

# Dictionary of folders based on extensions (map)
CATEGORIES = {
    'Images': ['.jpg', '.jpeg', '.gif', '.png', '.svg', '.ai', '.bmp', '.tiff', '.raw', '.heic', '.dng'],
    'Documents': ['.doc', '.docx', '.pdf', '.txt', '.md', '.ppt', '.xls', '.odt', '.rtf', '.tex', '.pages', '.tex'],
    'Code': ['.cpp', '.c', '.py', '.java', '.js', '.ts', '.sh', '.css', '.html', '.sass', '.rb', '.go', '.hs', '.lua', '.swift', '.cs', '.rust']
}

# Function that puts everyting that is not defined in CATEGORIES to Other.
def categorize_file(extension):
    for category, extensions in CATEGORIES.items():
        if extension in extensions:
            return category
    return 'Other'

# Function that moves file to destination
def move_file(src, destination):
    shutil.move(src, destination)
    print(f"Moved: {src} -> {destination}")

def main(directory):
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory.")
        sys.exit(1)

    # Making folders based on CATEGORIES. 
    # If Folders alredy exsist, it will skip
    for category in CATEGORIES.keys():
        os.makedirs(os.path.join(directory, category), exist_ok=True)

    os.makedirs(os.path.join(directory, 'Other'), exist_ok=True)

    # Walk through the directory and sub-directories
    for foldername, subfolders, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(foldername, filename)
            file_extension = os.path.splitext(filename)[1].lower()

            # Get category and destination path
            category = categorize_file(file_extension)
            dest_path = os.path.join(directory, category, filename)

            # If file is not already in its destination directory, move it
            if file_path != dest_path:
                move_file(file_path, dest_path)

def wrapper(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)
    return wrapped

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: directory_cleanup.py <path_to_directory>")
        sys.exit(1)

    wrapped = wrapper(main, sys.argv[1])
    execution_time = timeit.timeit(wrapped, number=1)
    
    print(f"\nScript executed in {execution_time:.2f} seconds.")
