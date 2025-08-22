# ========================================== #
# The Password Manager in the command prompt #
# ========================================== #

from getpass import getpass
import logging
import os

from colorama import Fore, Style

# import nessesary utils
from .utils import *


class ManagerCMD:
    def __init__(self, data_path: str = "", use_website_as_name: bool | None = None) -> None:
        self.settings_handler: SettingsHandler = SettingsHandler(data_path=data_path, use_website_as_name=use_website_as_name)
        if data_path:
            os.makedirs(data_path, exist_ok=True)
            self.data_path = data_path
            self.settings_handler.set("data_path", data_path)
        else:
            self.data_path: str = self.settings_handler.get("data_path")
        self.update_data_path(self.data_path, False)

        if not os.path.isfile(os.path.join(self.data_path, "master", "master_pass.pem")):
            self.renew_keys()

    def update_data_path(self, data_path: str, check: bool = True) -> None:
        self.passwords_path = os.path.join(data_path, "passwords")
        setup_logging(os.path.join(data_path, "log", "password_manager.log"), self.settings_handler.get("log_level"))
        if check: self.check_setup()

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
                copy_string(password)

            website: str = input("Website: ") or "n/a"
            notes: str = input("notes: ") or "n/a"

            if not (name and website):
                print(f"{Fore.YELLOW}Password must have a name or website to save!{Style.RESET_ALL}")
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
                salt=AES_key[1],
                use_website_as_name=False
            )

        except (IndexError, PermissionError, FileNotFoundError, ValueError):
            print(f"{Fore.RED}Invalid inputs! | Please try again{Style.RESET_ALL}")
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
            print(f"{Fore.RED}Invalid name or key! | Please try again{Style.RESET_ALL}") # TODO: Suggesting names
            logging.error(f"Invalid key or name for reading: {e}")

    def display_password(self, password: dict[str, str]) -> None:
        print()
        print(f"Username: {password['username']}")      # TODO: better displaying
        print(f"Password: {password['password']}")
        print(f"Website: {password['website']}")
        print(f"Notes: {password['notes']}")
        print()
        copy_string(password["password"])

    def ask_master_pass(self, validate_from: str) -> str:
        master_pass = getpass("Master Password: ").strip().replace(" ", "_")
        if self.validate_master_pass(master_pass, validate_from):
            return master_pass
        return ""

    def list_passwords(self) -> None:
        password_names: list[str] = os.listdir(self.passwords_path)
        self.password_names: list[str] = [password for password in password_names]

        print(f"{len(self.password_names)} Passwords:")
        print("\n".join(self.password_names) + "\n")

    def validate_master_pass(self, password_to_check: str, validate_from: str) -> bool:
        validator = ValidateMasterPassword(self.data_path, validate_from)

        return validator.validate(password_to_check)

    def load_keys(self, validate_from: str) -> tuple[bool, bytes, list[str, bytes]]:
        correct_master: str = self.ask_master_pass(validate_from)
        if not correct_master:
            self.wrong_master_entered()
            return self.load_keys(validate_from)

        fernet_key, AES_key_tuple = get_keys(self.data_path, correct_master)
        if not (fernet_key and AES_key_tuple):
            logging.warning(f"Unable to load keys | from: {validate_from}")
            self.renew_keys()
            return self.load_keys(validate_from)

        return (correct_master, fernet_key, list(AES_key_tuple))

    def wrong_master_entered(self) -> None:
        print(f"{Fore.RED}Wrong master Password entered!{Style.RESET_ALL}")

    def get_password_name(self) -> str:
        name = input("Name of the password: ").lower().replace(" ", "")
        while name not in self.password_names:
            name = input("Name of the password: ").lower().replace(" ", "")
            if name in ("quit", "back", "q"):
                return None
        return name

    def renew_keys(self) -> None:
        new_master: str = getpass("New master Password: ").strip().replace(" ", "_")
        if new_master:
            renew_keys_and_delete_paswords(new_master, self.data_path)
            self.reset_console()
        else:
            print("Renewing cancelled!")

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
        if copy_string(password):
            print(f"{Fore.GREEN}The password was copied to the clipboard!{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Copying was unsuccessfull. Please copy it manually{Style.RESET_ALL}")

        return password

    def import_passwords(self) -> None:
        try:
            correct, fernet_key, AES_key = self.load_keys("import_passwords")
            if not correct: return

            csv_file = input("File path for csv file: ")
            if not csv_file or not os.path.isfile(csv_file):
                print(f"{Fore.RED}Invalid file path entered!{Style.RESET_ALL}")
                return

            ImportPasswords(csv_file, self.passwords_path, (fernet_key, AES_key))
            self.list_passwords()

        except (IndexError, PermissionError, FileNotFoundError, ValueError, KeyError) as e:
            logging.error(f"Error while importing password: {e}")
            print(f"{Fore.RED}Saving unsuccessfull due to an Error{Style.RESET_ALL}")

    def export_passwords(self) -> None:
        try:
            correct, fernet_key, AES_key = self.load_keys("export_passwords")
            if not correct: return

            save_directory = input("Folder for saving csv file(path): ")
            if not save_directory or not os.path.isdir(save_directory):
                print(f"{Fore.RED}Invalid folder path entered!{Style.RESET_ALL}")
                return

            csv_file = os.path.join(save_directory, "passwords.csv")
            ExportPasswords(csv_file, self.passwords_path, (fernet_key, AES_key))

        except (IndexError, PermissionError, FileNotFoundError, ValueError, KeyError) as e:
            logging.error(f"Error while exporting password: {e}")
            print(f"{Fore.RED}Exporting unsuccessfull due to an Error{Style.RESET_ALL}")

    def search_passwords(self, query: str) -> None:
        """Searches for passwords that match the query.

        Args:
            query (str): The query that will be searched for.
        """
        search_result: list[str] = search_passwords(self.data_path, query)
        if len(search_result) == 1 and len(query) >= 5:
            self.read_password(search_result[0])
        else:
            print(f"{Fore.YELLOW}Unknown passowrd!{Style.RESET_ALL}")
            print("Did you mean: " + ", ".join(search_result))

    def remove_password(self, name) -> None:
        remove_password(self.data_path, name)
        print(f"{Fore.YELLOW}\"{name}\" has been removed{Style.RESET_ALL}")
