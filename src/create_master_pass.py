import hashlib
import logging
import json
import os

from .validate_master_pass import ValidateMasterPasswort


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
        master_pass: dict = {"hash": str(inputted_hash), "salt": str(self.salt), "iterations": self.iterations}
        self.save_master(master_pass)

        return self.validate(self.entered_password)

    def validate(self, password_to_check: str) -> bool:
        return ValidateMasterPasswort(self.data_path, "test-created").validate(password_to_check)

    def save_master(self, master_pass: dict) -> None:
        config_file: str = os.path.join(self.data_path, "master", "master_pass.pem")
        try:
            with open(config_file, "w") as file:
                json.dump(master_pass, file)

        except (FileNotFoundError, PermissionError) as e:
            logging.exception(f"Error saving master password: {e}")

    def hash_inputted(self, inputted: str, salt: str, iterations: int) -> str:
        return hashlib.pbkdf2_hmac(self.hashing_method, bytes(inputted, "utf-8"), salt, iterations)
