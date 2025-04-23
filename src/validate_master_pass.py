import hashlib
import logging
import json
import os
import ast

from .get_data_path import get_data_path


class ValidateMasterPasswort:
    def __init__(self, validate_from: str) -> None:
        self.data_path: str = get_data_path()
        self.validate_from: str = validate_from
        self.hashing_method: str = "sha512"

    def validate(self, password_to_check: str) -> bool:
        master_pass: list[str, str, int] = self.get_master()
        if not master_pass:
            self.record_attempt("incorrect", self.validate_from)
            return False

        master_pass[0] = ast.literal_eval(master_pass[0])
        master_pass[1] = ast.literal_eval(master_pass[1])
        inputted = self.hash_inputted(password_to_check, *master_pass[1:3])

        correct_pass: bool = self.is_Password_corect(master_pass[0], inputted)
        if correct_pass:
            self.record_attempt("correct", self.validate_from)
        elif not correct_pass:
            self.record_attempt("incorrect", self.validate_from)

        return correct_pass

    def get_master(self) -> list[bytes, bytes, int]:
        config_file: str = os.path.join(self.data_path, "master", "master_pass.pem")
        try:
            with open(config_file, "r") as file:
                config: dict[bytes, bytes, int] = json.loads(file.read()) # hash, salt, iterations

        except (FileNotFoundError, PermissionError):
            return None

        return list(config.values())

    def hash_inputted(self, inputted: str, salt: str, iterations: int) -> str:
        return hashlib.pbkdf2_hmac(self.hashing_method, bytes(inputted, "utf-8"), salt, iterations)

    def is_Password_corect(self, inputed, real) -> bool:
        return str(inputed) == str(real)

    def record_attempt(self, type: str, validate_from: str) -> None:
        if type == "incorrect":
            logging.warning(f"Worng master password entered | from {validate_from}")
        elif type == "correct":
            logging.info(f"Correct master password entered | from {validate_from}")
