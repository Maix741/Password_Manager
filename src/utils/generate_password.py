import logging
import string
import random

from cryptography.fernet import Fernet


class PasswordGenerator:
    def new_password(self, length: int, include_lower: bool, include_upper: bool, include_numbers: bool, include_special: bool) -> str:
        possible_characters: list[str] = self.possible_characters(include_lower, include_upper, include_numbers, include_special)

        if length < 3:
            length = 3

        meets_criteria: bool = False
        while not meets_criteria:
            password: list[str] = [random.choice(possible_characters) for _ in range(length)] # random.sample(possible_characters, length)
            meets_criteria = self.meets_criteria(password, include_lower, include_upper, include_numbers, include_special)
            password: str = "".join(password)

        return password

    def possible_characters(self, include_lower: bool, include_upper: bool, include_numbers: bool, include_special: bool) -> list[str]:
        possible_characters: list[str] = []

        if include_lower and not include_upper: 
            self.letters_lowercase: list[str] = [s for s in string.ascii_lowercase * 3]
        elif include_upper and not include_lower:
            self.letters_uppercase: list[str] = [s for s in string.ascii_uppercase * 3]
        else:
            self.letters_lowercase: list[str] = [s for s in string.ascii_lowercase]
            self.letters_uppercase: list[str] = [s for s in string.ascii_uppercase]

        self.numbers: list[str] = [s for s in string.digits * 2]
        self.special: list[str] = [s for s in r"""!"#$%&()*+-/<=>?@[\]^_{|}~"""]

        if include_lower: possible_characters += self.letters_lowercase
        if include_upper: possible_characters += self.letters_uppercase
        if include_numbers: possible_characters += self.numbers
        if include_special: possible_characters += self.special

        return possible_characters if possible_characters else (self.letters_lowercase + self.letters_uppercase)

    def meets_criteria(self, password: list[str],
                       include_lower: bool, include_upper: bool,
                       include_numbers: bool, include_special: bool) -> bool:
        has_lower: bool = (not include_lower) or (any(map(lambda x: x in self.letters_lowercase, password)))
        has_upper: bool = (not include_upper) or (any(map(lambda x: x in self.letters_uppercase, password)))
        has_number: bool = (not include_numbers) or (any(map(lambda x: x in self.numbers, password)))
        has_special: bool = (not include_special) or (any(map(lambda x: x in self.special, password)))
    
        return all([has_lower, has_upper, has_number, has_special])


def gen_aes_key() -> str:
    return generate_password(32, True, True, True, True)


def gen_fernet_key() -> bytes:
    return Fernet.generate_key()


def generate_password(length: int, include_lower: bool, include_upper: bool, include_numbers: bool, include_special: bool) -> str:
    generator: PasswordGenerator = PasswordGenerator()
    password: str = generator.new_password(length, include_lower, include_upper, include_numbers, include_special)

    return password


def get_password_length(minimum: int = 0) -> int:
    number: str = input("Lenght of the password: ")
    while not number.isdigit() or int(number) < minimum:
        number: str = input(f"Please enter a number above {minimum}!: ")

    return int(number)


def gen_password_cmd() -> str:
    logging.debug("Generating new password")
    length: int = get_password_length()
    include_lower: bool = input("Should the password include lowercase letters (y/n): ").lower().replace(" ", "") in ("y", "yes")
    include_upper: bool = input("Should the password include uppercase letters (y/n): ").lower().replace(" ", "") in ("y", "yes")
    include_numbers: bool = input("Should the password include numbers (y/n): ").lower().replace(" ", "") in ("y", "yes")
    include_special: bool = input("Should the password include special characters (y/n): ").lower().replace(" ", "") in ("y", "yes")

    return generate_password(length, include_lower, include_upper, include_numbers, include_special)
