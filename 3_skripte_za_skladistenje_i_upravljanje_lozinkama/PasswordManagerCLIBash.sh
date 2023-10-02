#!/bin/bash

# Initialize variables
LOG_FILE="password_manager.log"

# Function to log actions
log_action() {
    echo "$(date): $1" >> "$LOG_FILE"
}

# Function to encrypt file
encrypt_file() {
    if [ -f "$1" ]; then
        openssl enc -aes-256-cbc -pbkdf2 -iter 100000 -salt -in "$1" -out "$1.enc" -k "$2"
        mv "$1.enc" "$1"
    else
        echo "File not found: $1"
    fi
}

# Function to decrypt file
decrypt_file() {
    if [ -f "$1" ]; then
        openssl enc -aes-256-cbc -pbkdf2 -iter 100000 -d -in "$1" -out "$1.dec" -k "$2"
        mv "$1.dec" "$1"
    else
        echo "File not found: $1"
    fi
}

# Function to check password complexity
check_password_complexity() {
    if [[ ${#1} -ge 6 && "$1" =~ [A-Z] && "$1" =~ [0-9] && "$1" =~ [^a-zA-Z0-9] ]]; then
        return 0
    else
        return 1
    fi
}

# Function to generate a strong password
generate_strong_password() {
    echo "$(openssl rand -base64 12 | tr -d '=' | tr 'A-Za-z' 'N-ZA-Mn-za-m')0A!"
}

# Function to import passwords
import_passwords() {
    read -p "Specify the location of the file to import: " import_file
    if [ ! -f "$import_file" ]; then
        echo "File does not exist: $import_file"
        return
    fi

    imported_username=$(grep "username:" "$import_file" | cut -d ' ' -f 2)
    imported_master_password=$(grep "master_password:" "$import_file" | cut -d ' ' -f 2)
    PASSWORD_FILE="${imported_username}_passwords.enc"

    if [ ! -f "$PASSWORD_FILE" ]; then
        echo "No existing account matches the imported username."
        return
    fi

    decrypt_file "$PASSWORD_FILE" "$imported_master_password"
    grep -E '{|}' -A 1000 "$import_file" | sed '/{/d' | sed '/}/d' >> "$PASSWORD_FILE"
    encrypt_file "$PASSWORD_FILE" "$imported_master_password"

    log_action "Imported passwords for $imported_username."
    echo "Passwords imported successfully."
}

# Function to export passwords
export_passwords() {
    read -p "Enter your username: " username
    read -sp "Enter your master password: " master_password
    echo
    PASSWORD_FILE="${username}_passwords.enc"
    decrypt_file "$PASSWORD_FILE" "$master_password"

    if [ -f "$PASSWORD_FILE" ]; then
        export_file="${username}_passwords.txt"
        cp "$PASSWORD_FILE" "$export_file"
        encrypt_file "$PASSWORD_FILE" "$master_password"
        log_action "Exported all passwords for $username to $export_file."
        echo "Passwords exported successfully to $export_file."
    else
        echo "Invalid username or master password. Please try again."
    fi
}

# Main menu
while true; do
    echo "Password Manager CLI"
    echo "1. Setup Account"
    echo "2. Add Password to an Account"
    echo "3. Retrieve Passwords"
    echo "4. Update Password"
    echo "5. Delete Password"
    echo "6. Import Passwords"
    echo "7. Export Passwords"
    echo "8. Exit"
    read -p "Choose an option: " option

    case $option in
        1)
            read -p "Enter a username: " username
            PASSWORD_FILE="${username}_passwords.enc"
            if [ -f "$PASSWORD_FILE" ]; then
                echo "Username already exists. Choose a different username."
                continue
            fi
            read -p "Would you like to generate a strong master password? (y/n): " generate_option
            if [[ "$generate_option" == "y" || "$generate_option" == "Y" ]]; then
                master_password=$(generate_strong_password)
                echo "Generated master password: $master_password"
            else
                read -sp "Set up your master password: " master_password
                echo
            fi

            if check_password_complexity "$master_password"; then
                touch "$PASSWORD_FILE"
                encrypt_file "$PASSWORD_FILE" "$master_password"
                log_action "Account setup completed for $username."
            else
                echo "Password does not meet complexity requirements."
                echo "It must have at least 6 characters, one capital letter, one number, and one special character."
            fi
            ;;
        2)
            read -p "Enter your username: " username
            read -sp "Enter your master password: " master_password
            echo
            PASSWORD_FILE="${username}_passwords.enc"
            decrypt_file "$PASSWORD_FILE" "$master_password"
            read -p "Enter the label for the password: " label
            read -sp "Enter the password to store: " password_to_store
            echo
            echo "$label: $password_to_store" >> "$PASSWORD_FILE"
            encrypt_file "$PASSWORD_FILE" "$master_password"
            log_action "Stored password for $label under $username."
            ;;
        3)
            read -p "Enter your username: " username
            read -sp "Enter your master password: " master_password
            echo
            PASSWORD_FILE="${username}_passwords.enc"
            decrypt_file "$PASSWORD_FILE" "$master_password"
            cat "$PASSWORD_FILE"
            encrypt_file "$PASSWORD_FILE" "$master_password"
            log_action "Retrieved all passwords for $username."
            ;;
        4)
            read -p "Enter your username: " username
            read -sp "Enter your master password: " master_password
            echo
            PASSWORD_FILE="${username}_passwords.enc"
            decrypt_file "$PASSWORD_FILE" "$master_password"
            read -p "Enter the label of the password you want to update: " label
            existing_password=$(grep "$label: " "$PASSWORD_FILE" | cut -d ' ' -f 2-)
            if [ -z "$existing_password" ]; then
                echo "No password found for the label $label."
            else
                read -sp "Enter the new password: " new_password
                echo
                sed -i "s/$label: $existing_password/$label: $new_password/" "$PASSWORD_FILE"
            fi
            encrypt_file "$PASSWORD_FILE" "$master_password"
            log_action "Updated password for $label under $username."
            ;;
        5)
            read -p "Enter your username: " username
            read -sp "Enter your master password: " master_password
            echo
            PASSWORD_FILE="${username}_passwords.enc"
            decrypt_file "$PASSWORD_FILE" "$master_password"
            read -p "Enter the label of the password you want to delete: " label
            existing_password=$(grep "$label: " "$PASSWORD_FILE" | cut -d ' ' -f 2-)
            if [ -z "$existing_password" ]; then
                echo "No password found for the label $label."
            else
                sed -i "/$label: $existing_password/d" "$PASSWORD_FILE"
            fi
            encrypt_file "$PASSWORD_FILE" "$master_password"
            log_action "Deleted password for $label under $username."
            ;;
        6)
            import_passwords
            ;;
        7)
            export_passwords
            ;;
        8)
            exit 0
            ;;
        *)
            echo "Invalid option. Try again."
            ;;
    esac
done
