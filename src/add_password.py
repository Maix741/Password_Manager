import json
import os
import re

from .encryption_handlers import AESCrypto, FernetCrypto


class AddPassword:
    def __init__(self,
                 username: str, password: str, notes: str, name: str, website: str,
                 passwords_path: str, replace: bool,
                 fernet_key: bytes, AES_key: str, salt: bytes
                 ) -> None:

        if not name:
            if "www." in website:
                name: str = ".".join(website.split(".")[1:2].split("/")[0])
            else:
                name: str = ".".join(website.split(".")[0:1].split("/")[0])

        name = re.sub(r'[\\/*?:"<>|]', "", name)
        password_path: str = os.path.join(passwords_path, f"{name}.json")
        password_to_add: dict[str, str] = {
                                "username": self.encrypt_string(username, AES_key, salt, fernet_key),
                                "password": self.encrypt_string(password, AES_key, salt, fernet_key),
                                "notes": self.encrypt_string(notes, AES_key, salt, fernet_key),
                                "website": str(website)
                                }

        self.write_json(password_path, password_to_add, replace)

    def write_json(self, file_path, password_dict: dict, replace: bool) -> None:
        i: int = 0
        while os.path.isfile(file_path) and not replace:
            i += 1
            file_path: str = os.path.splitext(file_path)[0] + f"{i}.json"

        with open(file_path, "w") as password_file:
            json.dump(password_dict, password_file)

    def encrypt_string(self, text: str, AES_key: str, salt: bytes, fernet_key: bytes) -> str:
        aes_obj: AESCrypto = AESCrypto()
        fer_obj: FernetCrypto = FernetCrypto()

        first_encription: str = aes_obj.encrypt(text, AES_key, salt)
        second_encryption: str = fer_obj.encrypt(first_encription, fernet_key)

        return second_encryption
