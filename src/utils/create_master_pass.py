import hashlib
import logging
import os

from .validate_master_pass import ValidateMasterPassword


class CreateMasterPassword:
    def __init__(self, data_path: str, entered_password: str) -> None:
        self.data_path = data_path
        logging.info("Creating New Master password...")

        self.entered_password: str = entered_password
        self.salt: bytes = os.urandom(16)
        self.iterations: int = 300000
        self.hashing_method: str = "sha512"

    def create(self) -> bool:
        inputted_hash: bytes = self.hash_inputted(self.entered_password, self.salt, self.iterations)
        self.save_master(f'{inputted_hash.hex()}\n{self.salt.hex()}\n{self.iterations}')

        return self.validate(self.entered_password)

    def validate(self, password_to_check: str) -> bool:
        return ValidateMasterPassword(self.data_path, "test-created").validate(password_to_check)

    def save_master(self, master_pass: str) -> None:
        master_file: str = os.path.join(self.data_path, "master", "master_pass.pem")
        try:
            with open(master_file, "w") as file:
                file.write(master_pass)

        except (FileNotFoundError, PermissionError) as e:
            logging.exception(f"Error saving master password: {e}")

    def hash_inputted(self, inputted: str, salt: str, iterations: int) -> str:
        return hashlib.pbkdf2_hmac(self.hashing_method, bytes(inputted, "utf-8"), salt, iterations)
