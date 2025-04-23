import json
import os

from .encryption_handlers.fernet_crypto import FernetCrypto
from .encryption_handlers.aes_crypto import AESCrypto


class PasswordReader:
    def read_password(self, name: str, AES_key: str, salt: bytes, fernet_key: bytes, password_path: str):
        password_path = os.path.join(password_path, f"{name}.json")

        password_to_read: dict[str, str] = self.read_json(password_path)

        for key, value in password_to_read.items():
            if key == "website":
                break
            password_to_read[key] = self.decrypt_string(value, AES_key, salt, fernet_key)

        return password_to_read

    def decrypt_string(self, text: str, AES_key: str, salt: bytes, fernet_key: bytes) -> str:
        aes_obj: AESCrypto = AESCrypto()
        fer_obj: FernetCrypto = FernetCrypto()

        first_decription: str = fer_obj.decrypt(text, fernet_key)
        second_decryption: str = aes_obj.decrypt(first_decription, AES_key, salt)

        return second_decryption

    def read_json(self, file_path) -> str:
        with open(file_path, "r") as password_file:
            password_to_read: str = json.load(password_file)
        
        return password_to_read
