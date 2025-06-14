import logging
import io, csv

from .add_password import AddPassword


class ImportPasswords:
    def __init__(self, csv_file_path: str, passwords_path: str, keys: tuple[bytes, list[bytes]]) -> None:
        self.passwords_path = passwords_path
        passwords: list[str] = self.read_file(csv_file_path)
        passwords: list[tuple[str]] = map(self.csv_to_list, passwords)
        self.add_all_passwords(list(passwords), keys)

    def add_all_passwords(self, passwords: list[tuple[str]], keys: tuple[bytes, list[bytes]]) -> None:
        for i, password in enumerate(passwords):
            name, website, username, passwd, note = password
            password: dict[str, str] = {
                "name": name,
                "username": username,
                "password": passwd,
                "website": website,
                "notes": note
            }
            logging.info(f"Adding Password({i+1}/{len(passwords)}): {password['name']} ")
            self.add_password(password, *keys)

    def read_file(self, csv_file_path: str) -> list[str]:
        with open(csv_file_path, "r") as csv_file:
            lines: list[str] = csv_file.readlines()[1:]

        return lines

    def add_password(self, password: dict[str, str], fernet_key: bytes, AES_key: list[bytes]) -> None:
        AddPassword(
            name=password["name"],
            username=password["username"],
            password=password["password"],
            notes=password["notes"],
            website=password["website"],
            passwords_path=self.passwords_path,
            replace=False,
            fernet_key=fernet_key,
            AES_key=AES_key[0],
            salt=AES_key[1],
            use_website_as_name=False
        )

    def csv_to_list(self, input_string: str) -> list[str]:
        # Use StringIO to treat the string as a file-like object.
        f = io.StringIO(input_string)
        reader = csv.reader(f)
        # Get the first (and only) row from the CSV reader.
        return tuple(next(reader))
