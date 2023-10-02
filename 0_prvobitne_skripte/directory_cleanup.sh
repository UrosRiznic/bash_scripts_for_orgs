#!/bin/bash

# $1 is argument folder path that we sent during the call of script.
# This just checks if the dir is valid and if exsists.
# ! means if its not...
# -d means directory
# exit 1 means exit the script.
if [[ ! -d "$1" ]]; then
    echo "Error: $1 is not a valid directory."
    exit 1
fi

# This function takes 1 argument (a file name)
# and checks its extension. 
# When it detects extension, it returns the category.
detect_extension() {
    case "$1" in
        *.jpg | *.jpeg | *.gif | *.png | *.svg | *.bmp | *.tiff | *.ico | *.raw | *.webp | *.ai | *.heic | *.dng ) echo "Images" ;;
        *.doc | *.docx | *.pdf | *.txt | *.md | *.ppt | *.xls | *.png | *.odt | *.ods | *.rtf | *.tex | *.pages | *.keys | *.rtf ) echo "Documents" ;;
        *.cpp | *.c | *.py | *.cs | *.java | *.js | *.ts | *.sh | *.css | *.html | *.sass | *.cpp | *.go | *.hs | *.lua | *.sql | *.rb | *.swift | *.rust ) echo "Code" ;;
        *) echo "Other" ;;
    esac
}

# IFS (Internal Field Separator) is special variable that tells bash
# how separator looks and it helps bash to recognize folders with spaces inside the name.
IFS=$'\n'

# mkdir creates directories
# -p will create parent directorie and wont throw an error if the directory alredy exsists.
mkdir -p "$1/Images" "$1/Documents" "$1/Code" "$1/Other"

# Using the find function to find all files in directory
# and for each file we do the logic.
find "$1" -type f | while read -r file; do
    # Getting files category
    category=$(detect_extension "$file")

    # Getting file destination
    # basename = command that extracts just the file name from full path
    dest="$1/$category/$(basename "$file")"

    # Last thing is moving files to corresponding destination. 
    # If they are not alredy in correct destination.
    if [[ "$file" != "$dest" ]]; then
        mv "$file" "$dest"
        echo "Moved: $file -> $dest"
    fi
done
