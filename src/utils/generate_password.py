import logging
import string
import random

from cryptography.fernet import Fernet


class PasswordGenerator:
    def new_password(self, lenght: int, include_letters: bool = True, include_numbers: bool = True, include_special: bool = True) -> str:
        possible_characters: list[str] = self.possible_characters(include_letters, include_numbers, include_special)

        if lenght < 3:
            lenght = 3

        meets_criteria: bool = False
        while not meets_criteria:
            password: list[str] = [random.choice(possible_characters) for _ in range(lenght)] # random.sample(possible_characters, lenght)
            meets_criteria = self.meets_criteria(password, include_letters, include_numbers, include_special)
            password: str = "".join(password)

        return password

    def possible_characters(self, include_Letters: bool, include_Numbers: bool, include_Special: bool) -> str:
        possible_characters: list[str] = []
        self.letters: list[str] = [s for s in string.ascii_letters * 3]
        self.numbers: list[str] = [s for s in string.digits * 2]
        self.special: list[str] = [s for s in r"""!"#$%&()*+-/<=>?@[\]^_{|}~"""]

        if include_Letters: possible_characters += self.letters
        if include_Numbers: possible_characters += self.numbers
        if include_Special: possible_characters += self.special

        return possible_characters if possible_characters else self.letters

    def meets_criteria(self, password: list[str], include_letters: bool, include_numbers: bool, include_special: bool) -> bool:
        has_letter: bool = (not include_letters) or (any(map(lambda x: x in self.letters, password)))
        has_number: bool = (not include_numbers) or (any(map(lambda x: x in self.numbers, password)))
        has_special: bool = (not include_special) or (any(map(lambda x: x in self.special, password)))
    
        return all([has_letter, has_number, has_special])


def gen_aes_key() -> str:
    return generate_password(32, True, True, True)


def gen_fernet_key() -> bytes:
    return Fernet.generate_key()


def generate_password(lenght: int, include_letters: bool, include_numbers: bool, include_special: bool) -> str:
    generator: PasswordGenerator = PasswordGenerator()
    password: str = generator.new_password(lenght, include_letters, include_numbers, include_special)

    return password


def get_password_lenght(minimum: int = 0) -> int:
    number: str = input("Lenght of the password: ")
    while not number.isdigit() or int(number) < minimum:
        number: str = input(f"Please enter a number above {minimum}!: ")

    return int(number)


def gen_password_cmd() -> str:
    logging.debug("Generating new password")
    lenght: int = get_password_lenght()
    include_letters: bool = input("Should the password include letters (y/n): ").lower().replace(" ", "") in ("y", "yes")
    include_numbers: bool = input("Should the password include numbers (y/n): ").lower().replace(" ", "") in ("y", "yes")
    include_special: bool = input("Should the password include special characters (y/n): ").lower().replace(" ", "") in ("y", "yes")

    return generate_password(lenght, include_letters, include_numbers, include_special)
