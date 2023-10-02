#!/usr/bin/env python3

import os
import subprocess
import getpass

LOG_FILE = "password_manager.log"


def log_action(message):
    with open(LOG_FILE, 'a') as log:
        log.write(f"{subprocess.check_output('date').decode('utf-8').strip()}: {message}\n")


def encrypt_file(file_path, password):
    if os.path.exists(file_path):
        subprocess.run(['openssl', 'enc', '-aes-256-cbc', '-pbkdf2', '-iter', '100000', '-salt',
                        '-in', file_path, '-out', f"{file_path}.enc", '-k', password])
        os.rename(f"{file_path}.enc", file_path)
    else:
        print(f"File not found: {file_path}")


def decrypt_file(file_path, password):
    if os.path.exists(file_path):
        result = subprocess.run(['openssl', 'enc', '-aes-256-cbc', '-pbkdf2', '-iter', '100000', '-d',
                                 '-in', file_path, '-out', f"{file_path}.dec", '-k', password],
                                stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        if result.returncode != 0:
            if b"bad decrypt" in result.stderr:
                print("Invalid master password. Please try again.")
                return False
            else:
                print("An error occurred during decryption.")
                return False
        os.rename(f"{file_path}.dec", file_path)
        return True
    else:
        print(f"File not found: {file_path}")
        return False


def check_password_complexity(password):
    if (len(password) >= 6 and any(char.isupper() for char in password) and
            any(char.isdigit() for char in password) and not password.isalnum()):
        return True
    return False


def generate_strong_password():
    random_data = subprocess.check_output(
        ['openssl', 'rand', '-base64', '12']).decode('utf-8').strip()
    transformed_data = random_data.translate(
        str.maketrans('A-Za-z', 'N-ZA-Mn-za-m')).rstrip('=')
    return f"{transformed_data}0A!"


def import_passwords():
    import_file = input("Specify the location of the file to import: ")
    if not os.path.exists(import_file):
        print(f"File does not exist: {import_file}")
        return

    with open(import_file, 'r') as f:
        content = f.read()

    imported_username = None
    imported_master_password = None

    for line in content.split("\n"):
        if "username:" in line:
            imported_username = line.split()[1]
        if "master_password:" in line:
            imported_master_password = line.split()[1]

    PASSWORD_FILE = f"{imported_username}_passwords.enc"
    if not os.path.exists(PASSWORD_FILE):
        print(f"No existing account matches the imported username.")
        return

    decrypt_file(PASSWORD_FILE, imported_master_password)
    with open(PASSWORD_FILE, 'a') as pf:
        pf.write("\n".join([line for line in content.split(
            "\n") if '{' not in line and '}' not in line and 'username:' not in line and 'master_password:' not in line]))
    encrypt_file(PASSWORD_FILE, imported_master_password)

    log_action(f"Imported passwords for {imported_username}.")
    print("Passwords imported successfully.")


def export_passwords():
    username = input("Enter your username: ")
    master_password = getpass.getpass("Enter your master password: ")
    PASSWORD_FILE = f"{username}_passwords.enc"
    decrypt_file(PASSWORD_FILE, master_password)

    if os.path.exists(PASSWORD_FILE):
        export_file = f"{username}_passwords.txt"
        with open(PASSWORD_FILE, 'r') as pf, open(export_file, 'w') as ef:
            ef.write(pf.read())
        encrypt_file(PASSWORD_FILE, master_password)
        log_action(f"Exported all passwords for {username} to {export_file}.")
        print(f"Passwords exported successfully to {export_file}.")
    else:
        print("Invalid username or master password. Please try again.")


while True:
    print("Password Manager CLI")
    print("1. Setup Account")
    print("2. Add Password to an Account")
    print("3. Retrieve Passwords")
    print("4. Update Password")
    print("5. Delete Password")
    print("6. Import Passwords")
    print("7. Export Passwords")
    print("8. Exit")

    option = input("Choose an option: ")

    if option == '1':
        username = input("Enter a username: ")
        PASSWORD_FILE = f"{username}_passwords.enc"
        if os.path.exists(PASSWORD_FILE):
            print("Username already exists. Choose a different username.")
            continue
        generate_option = input("Would you like to generate a strong master password? (y/n): ")
        if generate_option.lower() == "y":
            master_password = generate_strong_password()
            print(f"Generated master password: {master_password}")
        else:
            master_password = getpass.getpass("Set up your master password: ")

        if check_password_complexity(master_password):
            open(PASSWORD_FILE, 'a').close()
            encrypt_file(PASSWORD_FILE, master_password)
            log_action(f"Account setup completed for {username}.")
        else:
            print("Password does not meet complexity requirements.")
            print("It must have at least 6 characters, one capital letter, one number, and one special character.")

    elif option == '2':
        username = input("Enter your username: ")
        master_password = getpass.getpass("Enter your master password: ")
        PASSWORD_FILE = f"{username}_passwords.enc"
        
        if not decrypt_file(PASSWORD_FILE, master_password):
            continue
        
        label = input("Enter the label for the password: ")
        
        with open(PASSWORD_FILE, 'r') as pf:
            lines = pf.readlines()
            existing_labels = [line.split(":")[0].strip() for line in lines]
            
            while label in existing_labels:
                print(f"The label '{label}' already exists. Choose a different label.")
                label = input("Enter a new label for the password: ")
        
        password_to_store = input("Enter the password to store: ")
        with open(PASSWORD_FILE, 'a') as pf:
            pf.write(f"{label}: {password_to_store}\n")
        encrypt_file(PASSWORD_FILE, master_password)
        log_action(f"Stored password for {label} under {username}.")

    elif option == '3':
        username = input("Enter your username: ")
        master_password = getpass.getpass("Enter your master password: ")
        PASSWORD_FILE = f"{username}_passwords.enc"
        
        if not decrypt_file(PASSWORD_FILE, master_password):
            continue
        
        with open(PASSWORD_FILE, 'r') as pf:
            print(pf.read())
        encrypt_file(PASSWORD_FILE, master_password)
        log_action(f"Retrieved all passwords for {username}.")

    elif option == '4':
        username = input("Enter your username: ")
        master_password = getpass.getpass("Enter your master password: ")
        PASSWORD_FILE = f"{username}_passwords.enc"
        
        if not decrypt_file(PASSWORD_FILE, master_password):
            continue
        
        label = input("Enter the label of the password you want to update: ")
        with open(PASSWORD_FILE, 'r') as pf:
            lines = pf.readlines()
        for i, line in enumerate(lines):
            if line.startswith(f"{label}: "):
                new_password = input("Enter the new password: ")
                lines[i] = f"{label}: {new_password}\n"
                break
        else:
            print(f"No password found for the label {label}.")
            continue
        with open(PASSWORD_FILE, 'w') as pf:
            pf.writelines(lines)
        encrypt_file(PASSWORD_FILE, master_password)
        log_action(f"Updated password for {label} under {username}.")

    elif option == '5':
        username = input("Enter your username: ")
        master_password = getpass.getpass("Enter your master password: ")
        PASSWORD_FILE = f"{username}_passwords.enc"
        
        if not decrypt_file(PASSWORD_FILE, master_password):
            continue
        
        label = input("Enter the label of the password you want to delete: ")
        with open(PASSWORD_FILE, 'r') as pf:
            lines = pf.readlines()
        lines = [line for line in lines if not line.startswith(f"{label}: ")]
        with open(PASSWORD_FILE, 'w') as pf:
            pf.writelines(lines)
        encrypt_file(PASSWORD_FILE, master_password)
        log_action(f"Deleted password for {label} under {username}.")

    elif option == '6':
        import_passwords()

    elif option == '7':
        export_passwords()

    elif option == '8':
        break

    else:
        print("Invalid option. Try again.")
