# ========================================== #
# The Password Manager in the command prompt #
# ========================================== #

from getpass import getpass
import logging
import shutil
import os

import pyperclip

# import nessesary utils
from .utils import *


class ManagerCMD:
    def __init__(self) -> None:
        self.data_path: str = get_data_path()
        self.passwords_path: str = os.path.join(self.data_path, "passwords")

        setup_logging(os.path.join(self.data_path, "log", "password_manager.log"))
        self.reset_console()
        if not os.path.isfile(os.path.join(self.data_path, "master", "master_pass.pem")):
            self.renew_keys()

    def add_password(self) -> None:
        try:
            correct, fernet_key, AES_key = self.load_keys("add_password")
            if not correct:
                self.wrong_master_entered()
                return

            name: str = input("Name: ").lower()
            username: str = input("Username: ") or "n/a"
            password: str = getpass("Password: ")
            if not password:
                password: str = gen_password_cmd()
                pyperclip.copy(password)

            website: str = input("Website: ") or "n/a"
            notes: str = input("notes: ") or "n/a"

            if not (name and website):
                print("Password must have a name or website to save!")
                return

            logging.info(f"Adding Password: {name}")
            AddPassword(
                name=name,
                username=username,
                password=password,
                notes=notes,
                website=website,
                passwords_path=self.passwords_path,
                replace=False,
                fernet_key=fernet_key,
                AES_key=AES_key[0],
                salt=AES_key[1]
            )

        except (IndexError, PermissionError, FileNotFoundError, ValueError):
            print("Invalid inputs! | Please try again")
            return self.add_password()

    def read_password(self, name: str) -> None:
        try:
            correct, fernet_key, AES_key = self.load_keys("read_password")
            if not correct: raise Exception
            logging.info(f"Reading password: {name}")
            reader = PasswordReader()
            decrypted_password: dict[str, str] = reader.read_password(
                name=name, AES_key=AES_key[0], salt=AES_key[1], fernet_key=fernet_key, password_path=self.passwords_path
            )
            self.display_password(decrypted_password)

        except Exception as e:
            print("Invalid name or key! | Please try again") # TODO: Suggesting names
            logging.error(f"Invalid key or name for reading: {e}")

    def display_password(self, password: dict[str, str]) -> None:
        print()
        print(f"Username: {password["username"]}")      # TODO: better displaying
        print(f"Password: {password["password"]}")
        print(f"Website: {password["website"]}")
        print(f"Notes: {password["notes"]}")
        print()
        pyperclip.copy(password["password"])

    def ask_master_pass(self, validate_from: str) -> str:
        master_pass = getpass("Master Password: ").strip().replace(" ", "_")
        if self.validate_master_pass(master_pass, validate_from):
            return master_pass
        return ""

    def list_passwords(self) -> None:
        password_names: list[str] = os.listdir(self.passwords_path)
        self.password_names: list[str] = [os.path.splitext(password)[0] for password in password_names]

        print(f"{len(self.password_names)} Passwords:")
        print("\n".join(self.password_names) + "\n")

    def validate_master_pass(self, password_to_check: str, validate_from: str) -> bool:
        validator = ValidateMasterPasswort(self.data_path, validate_from)

        return validator.validate(password_to_check)

    def load_keys(self, validate_from: str) -> tuple[bool, bytes, list[str, bytes]]:
        correct_master: str = self.ask_master_pass(validate_from)
        if not correct_master:
            self.wrong_master_entered()
            return self.load_keys(validate_from)

        master_key_fragment: str = get_master_key_fragment(correct_master)


        fernet_key, AES_key_fragment = get_keys(self.data_path)
        if not (fernet_key and AES_key_fragment):
            logging.warning(f"Unable to load keys | from: {validate_from}")
            self.renew_keys()
            return self.load_keys(validate_from)

        AES_key, salt = master_key_fragment + AES_key_fragment[0], AES_key_fragment[1]
        fernet_key: bytes = fernet_key

        return (correct_master, fernet_key, [AES_key, salt])

    def wrong_master_entered(self) -> None:
        print("Wrong master Password entered!")

    def get_password_name(self) -> str:
        name = input("Name of the password: ").lower().replace(" ", "")
        while name not in self.password_names:
            name = input("Name of the password: ").lower().replace(" ", "")
            if name in ("quit", "back", "q"):
                return None
        return name

    def renew_keys(self) -> None:
        logging.info("Renewing all keys")
        try:
            shutil.rmtree(self.passwords_path)
            shutil.rmtree(os.path.join(self.data_path, "master"))
            shutil.rmtree(os.path.join(self.data_path, "keys"))

        except (FileNotFoundError, PermissionError) as e:
            logging.error(f"Error while removing previous keys/passwords: {e}")
        setup_folders(self.data_path)

        new_master: str = getpass("New master Password: ").strip().replace(" ", "_")
        CreateMasterPassword(self.data_path, new_master).create()

        _, _, aes_fragment = gen_aes_key(new_master)
        write_keys(self.data_path, aes_fragment)
        self.reset_console()

    def reset_console(self) -> None:
        self.clear_console()
        self.list_passwords()

    def clear_console(self) -> None:
        print("\033[H\033[J", end="")

    def check_setup(self) -> None:
        setup_correct: bool = check_setup(self.data_path)
        if setup_correct: logging.debug(f"Setup correct: {setup_correct}")
        elif not setup_correct: logging.warning(f"Setup correct: {setup_correct}")
        if not setup_correct: self.__init__()

    def gen_password(self) -> str:
        password: str = gen_password_cmd()
        self.reset_console()
        print(f"Generated password: {password}")
        print("The password was copied to the clipboard!")
        pyperclip.copy(password)

        return password

    def import_passwords(self) -> None:
        try:
            correct, fernet_key, AES_key = self.load_keys("import_passwords")
            if not correct: return

            csv_file = input("File path for csv file: ")
            if not csv_file or not os.path.isfile(csv_file):
                print("Invalid file path entered!")
                return

            ImportPasswords(csv_file, self.passwords_path, (fernet_key, AES_key))
            self.list_passwords()

        except (IndexError, PermissionError, FileNotFoundError, ValueError, KeyError) as e:
            logging.error(f"Error while importing password: {e}")
            print("Saving unsuccessfull due to an Error")

    def export_passwords(self) -> None:
        try:
            correct, fernet_key, AES_key = self.load_keys("export_passwords")
            if not correct: return

            save_directory = input("Folder for saving csv file(path): ")
            if not save_directory or not os.path.isdir(save_directory):
                print("Invalid folder path entered!")
                return

            csv_file = os.path.join(save_directory, "passwords.csv")
            ExportPasswords(csv_file, self.passwords_path, (fernet_key, AES_key))

        except (IndexError, PermissionError, FileNotFoundError, ValueError, KeyError) as e:
            logging.error(f"Error while exporting password: {e}")
            print("Exporting unsuccessfull due to an Error")
