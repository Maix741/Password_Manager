import logging
import csv
import os

from .read_password import PasswordReader


class ExportPasswords:
    def __init__(self, csv_file_path: str, passwords_path: str, keys: tuple[bytes, list[bytes]]) -> None:
        self.passwords_path = passwords_path

        password_names: list[str] = self.list_passwords()
        passwords: list[dict[str, str]] = self.read_all_passwords(password_names, keys)

        if csv_file_path:
            self.write_file(csv_file_path, passwords)
        elif not csv_file_path:
            self.passwords = passwords

    def return_as_list(self) -> list[dict[str, str]]:
        return self.passwords

    def read_all_passwords(self, password_names: list[str], keys: tuple[bytes, list[bytes]]) -> list[dict[str, str]]:
        passwords: list[tuple[str]] = []
        for i, name in enumerate(password_names):
            logging.info(f"Reading Password({i+1}/{len(password_names)}): {name} ")
            password: dict[str, str] = self.read_password(name, *keys)
            password["name"] = name
            passwords.append(password)

        return passwords

    def write_file(self, csv_file_path: str, file_lines: list[dict[str, str]]) -> None:
        """Writes the passwords to a CSV file.

        Args:
            csv_file_path (str): Path to the CSV file where passwords will be exported.
            file_lines (list[dict[str, str]]): List of dictionaries containing password data.
        """
        # change keys 'website' to 'url' and 'notes' to 'note', and remove the old keys
        file_lines = [
            {**{k: v for k, v in line.items() if k not in ("website", "notes")},
             "url": line.get("website", ""), "note": line.get("notes", "").strip()}
            for line in file_lines
        ]
        with open(csv_file_path, "w", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=["name", "url", "username", "password", "note"])
            writer.writeheader()
            # Write the file lines to the CSV file
            writer.writerows(file_lines)

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

    def list_passwords(self) -> list[str]:
        password_names: list[str] = os.listdir(self.passwords_path)
        return [os.path.splitext(password)[0] for password in password_names]
