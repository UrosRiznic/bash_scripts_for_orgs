#!/bin/bash

# Logging function
log() {
    echo "$(date): $1" >> "$TARGET_DIRECTORY/directory_cleanup.log"
}

# Accept the directory path as an argument
TARGET_DIRECTORY="$1"

# Prevent cleanup of critical folders
if [[ "$TARGET_DIRECTORY" == "/" || "$TARGET_DIRECTORY" == "/usr" || "$TARGET_DIRECTORY" == "/etc" || "$TARGET_DIRECTORY" == "/bin" ]]; then
    echo "This script cannot be run on critical system directories."
    exit 1
fi

# Check if the directory exists
# -d stands for directory
if [[ ! -d "$TARGET_DIRECTORY" ]]; then
    echo "Error: Directory does not exist."
    exit 1
fi

# Check if directory is empty
# -z stands for zero, in the context of, is this command zero/empty
if [[ -z "$(ls -A "$TARGET_DIRECTORY")" ]]; then
    echo "The directory is empty."
    exit 1
fi

# Initialize log file
log "Cleanup started."

# Create subdirectories
# -p stands for parents.
mkdir -p "$TARGET_DIRECTORY"/{Images,Documents,Video_and_Audio,Programs,Other,Files_without_extension}
log "Created subdirectories."

# Initialize summary message
SUMMARY="Summary of changes:\n"

# Main function that goes thrue whole directory and makes changes.
move_files() {
    for filepath in "$1"/*; do
        filename=$(basename -- "$filepath")
        
        # This line will check if filepath is directory, and if it is, 
        # it will recursivly call it self so it traverse true whole thing.
        if [[ -d "$filepath" ]]; then
            move_files "$filepath"
        else
            # Identify file type
            # -b means breafly ("povrsno")
            filetype=$(file -b -- "$filepath")
            
            destination=""
            
            # Logic for classification
            if [[ "$filetype" =~ image ]]; then
                destination="Images"
            elif [[ "$filetype" =~ text|PDF|"Microsoft Word"|"OpenDocument" ]]; then
                destination="Documents"
            elif [[ "$filetype" =~ audio|video ]]; then
                destination="Video_and_Audio"
            elif [[ "$filetype" =~ script || ( -x "$filepath" && "$filetype" =~ "executable" ) ]]; then
                destination="Programs"
            elif [[ "$filename" == *.* ]]; then
                destination="Other"
            else
                destination="Files_without_extension"
            fi

            # Move the file
            # This line checks if destination is set (if it is not null), and if it is
            # it moves the filepath to destination
            if [[ -n "$destination" ]]; then
                mv -- "$filepath" "$TARGET_DIRECTORY/$destination/"
                log "Moved: $filepath -> $TARGET_DIRECTORY/$destination/"
                SUMMARY+="$filepath -> $TARGET_DIRECTORY/$destination/\n"
            fi
        fi
    done
}

move_files "$TARGET_DIRECTORY"

# Delete empty directories
find "$TARGET_DIRECTORY" -type d -empty -exec rmdir {} + 
log "Removed empty directories."

# Print summary
echo -e "$SUMMARY"
log "Cleanup completed."
