import hashlib
import logging
import ast

from .get_master import get_master


class ValidateMasterPassword:
    def __init__(self, data_path, validate_from: str) -> None:
        self.data_path: str = data_path
        self.validate_from: str = validate_from
        self.hashing_method: str = "sha512"

    def validate(self, password_to_check: str) -> bool:
        master_pass: list[str, str, int] = get_master(self.data_path)
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

    def hash_inputted(self, inputted: str, salt: str, iterations: int) -> str:
        return hashlib.pbkdf2_hmac(self.hashing_method, bytes(inputted, "utf-8"), salt, iterations)

    def is_Password_corect(self, inputed, real) -> bool:
        return str(inputed) == str(real)

    def record_attempt(self, type: str, validate_from: str) -> None:
        if type == "incorrect":
            logging.warning(f"Worng master password entered | from {validate_from}")
        elif type == "correct":
            logging.info(f"Correct master password entered | from {validate_from}")
