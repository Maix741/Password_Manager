import logging
import os

from .read_password import PasswordReader


class ExportPasswords:
    def __init__(self, csv_file_path: str, passwords_path: str, keys: tuple[bytes, list[bytes]]) -> None:
        self.passwords_path = passwords_path

        password_names: list[str] = self.list_passwords()
        passwords: list[tuple[str]] = self.read_all_passwords(password_names, keys)
        password_strings: list[str] = self.transform_all(passwords)

        self.write_file(csv_file_path, password_strings)

    def read_all_passwords(self, password_names: list[str], keys: tuple[bytes, list[bytes]]) -> list[tuple[str]]:
        passwords: list[tuple[str]] = []
        for i, name in enumerate(password_names):
            logging.info(f"Reading Password({i+1}/{len(password_names)}): {name} ")
            password: dict[str, str] = self.read_password(name, *keys)
            passwords.append((name, password["website"], password["username"], password["password"], password["notes"]))

        return passwords

    def transform_all(self, passwords: list[tuple[str]]) -> list[str]:
        string_passwords: list[str] = []
        for password in passwords:
            string_password: str = self.tuple_to_string(password)
            string_passwords.append(string_password)

        return string_passwords

    def write_file(self, csv_file_path: str, file_lines: list[str]) -> list[str]:
        with open(csv_file_path, "w") as csv_file:
            csv_file.write("name,url,username,password,note\n")
            csv_file.write("\n".join(file_lines))

    def read_password(self, password_name: str, fernet_key: bytes, AES_key: list[bytes]) -> None:
        reader: PasswordReader = PasswordReader()
        password: dict[str, str] = reader.read_password(
            name=password_name,
            AES_key=AES_key[0],
            salt=AES_key[1],
            fernet_key=fernet_key,
            password_path=self.passwords_path,
        )
        return password

    def tuple_to_string(self, input_tuple: tuple) -> str:
        input_list: list[str] = list(input_tuple)
        for value in input_list:
            value2 = None
            if "," in value or "\"" in value:
                value2 = f"\"{value}\""

                index = input_list.index(value)
                input_list.pop(index)
                input_list.insert(index, value2)

        return ",".join(input_list)

    def list_passwords(self) -> list[str]:
        password_names: list[str] = os.listdir(self.passwords_path)
        return [os.path.splitext(password)[0] for password in password_names]
