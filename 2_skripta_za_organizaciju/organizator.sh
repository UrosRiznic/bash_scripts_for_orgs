#!/bin/bash

# Function to display progress
# Progress will be in green color 
show_progress() {
    echo -e "\e[32m[Progress]: $1\e[0m"
}

# Function to writes informations to file called organizer.log
# ">>" means append, while ">" means ovewrite
log_info() {
    echo "$(date +"%Y-%m-%d %H:%M:%S") - $1" >> organizer.log
}

# Recursive function to handle files in a directory and its subdirectories
# Function takes 2 arguments, current directory and target directory
# It loops thrue all files and directories inside current directory, 
# and it asks if the target directory is "folder". In that case, it calls itself and loops again.
#
organize_files() {
    local current_dir="$1"
    local target_dir="$2"
    for filepath in "$current_dir"/*; do
        if [ -d "$filepath" ]; then
            organize_files "$filepath" "$target_dir"

        # filepath -> ./some/path/to/the/script/fajl.extension
        # filename -> fajl.extension
        elif [ -f "$filepath" ]; then
            filename=$(basename -- "$filepath")
            
            # This part checks if the file has extension
            # This block checks if the filename has an extension. If it does, it extracts it. 
            # Otherwise, it uses "no_extension" as the extension.
            if [[ "$filename" == *.* ]]; then
                extension="${filename##*.}"
            else
                extension="no_extension"
            fi

            # mkdir -> make directory
            # -p    -> parent
            mkdir -p "$target_dir/$extension"
            dest="$target_dir/$extension/$filename"

            # This part helps for file collision.
            if [ "$filepath" == "$dest" ]; then
                continue
            fi

            # This part is triggered if the destination alredy exists,
            # in that case, it asks user to Overwrite, Skips or Rename the file.
            if [ -e "$dest" ]; then
                read -p "File $dest already exists. Overwrite/Skip/Rename? (o/s/r): " choice
                case "$choice" in
                    o)
                    ;;
                    s)
                    continue
                    ;;
                    r)
                    read -p "Enter new name: " new_name
                    dest="$target_dir/$extension/$new_name"
                    ;;
                    *)
                    echo "Invalid choice."
                    exit 1
                esac
            fi

            # based on the choice (move/copy) that user made, it takes an action
            if [ "$action" == "move" ]; then
                mv "$filepath" "$dest"
            else
                cp "$filepath" "$dest"
            fi

            log_info "$action: $filepath -> $dest"
            show_progress "$action: $filepath -> $dest"
        fi
    done
}

# Main part of the script

# Asks user to enter a source directory
read -p "Enter the source directory: " source_dir

# If directory doesnt exsist, it prints out message and exit the script
# -d     -> Directory
# exit 1 -> Exit from the program
if [ ! -d "$source_dir" ]; then
    echo "The directory does not exist."
    exit 1
fi

# Asking user if they want to move/copy
read -p "Do you want to move or copy files? (move/copy): " action

# This sets target directory to source directory
target_dir="$source_dir"

# If user chose copy as an option, first it makes folder
# COPY_OF_THE_FOLDER so that all material goes there
if [ "$action" == "copy" ]; then
    target_dir="$source_dir/COPY_OF_THE_FOLDER"
    mkdir -p "$target_dir"
fi

# Checks if the user entered a valid action. If not, it exits the script.
if [ "$action" != "move" ] && [ "$action" != "copy" ]; then
    echo "Invalid option."
    exit 1
fi

# Finds all files in the source_dir and organizes them by their extensions in target_dir.
find "$source_dir" -type f | while read -r file; do
    if [[ "$file" == *.* ]]; then
        extension="${file##*.}"
    else
        extension="no_extension"
    fi
    mkdir -p "$target_dir/$extension"
done

# Calling the function to move or copy the files
organize_files "$source_dir" "$target_dir"

# PART OF THE SCRIPT WHERE IT DOES CLEANUP AND LOGGING
show_progress "Checking for empty folders..."
empty_folders=$(find "$target_dir" -type d -empty)

# Checking if folder is empty
# -n means "null"
if [ -n "$empty_folders" ]; then
    echo "Found empty folders:"
    echo "$empty_folders"
    read -p "Do you want to remove these empty folders? (y/n): " remove_choice
    if [ "$remove_choice" == "y" ]; then
        echo "$empty_folders" | xargs rmdir
        log_info "Removed empty folders."
    else
        log_info "Empty folders kept."
    fi
else
    show_progress "No empty folders found."
fi

# Simple echo message
echo "Task completed. Check organizer.log for details."
