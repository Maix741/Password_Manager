import json
import os
import re

from .encryption_handlers import AESCrypto, FernetCrypto
from .transform_website import transform_website


class AddPassword:
    def __init__(self,
                 username: str, password: str, notes: str, name: str, website: str,
                 passwords_path: str, replace: bool,
                 fernet_key: bytes, AES_key: str, salt: bytes,
                 use_website_as_name: bool = False
                 ) -> None:

        if not name or use_website_as_name:
            name = transform_website(website)

        name = re.sub(r'[\\/*?:"<>|]', "", name)
        password_path: str = os.path.join(passwords_path, name)
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
            file_path: str = file_path + str(i)

        with open(file_path, "w") as password_file:
            json.dump(password_dict, password_file)

    def encrypt_string(self, text: str, AES_key: str, salt: bytes, fernet_key: bytes) -> str:
        aes_obj: AESCrypto = AESCrypto()
        fer_obj: FernetCrypto = FernetCrypto()

        first_encription: str = aes_obj.encrypt(text, AES_key, salt)
        second_encryption: str = fer_obj.encrypt(first_encription, fernet_key)

        return second_encryption
