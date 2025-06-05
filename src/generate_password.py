import logging
import string
import random


class PasswordGenerator:
    def new_password(self, min_lenght: int, include_letters: bool = True, include_numbers: bool = True, include_special: bool = True) -> str:
        possible_characters: str = self.possible_characters(include_letters, include_numbers, include_special)

        password: str = ""
        meets_criteria: bool = False
        has_lenght: bool = False
        has_letter: bool = not include_letters
        has_number: bool = not include_numbers
        has_special: bool = not include_special

        while not meets_criteria:
            new_letter: str = random.choice(possible_characters)
            password += new_letter

            if len(password) >= min_lenght:
                has_lenght = True
            if new_letter in self.letters:
                has_letter = True
            if new_letter in self.numbers:
                has_number = True
            if new_letter in self.special:
                has_special = True
            if has_lenght and has_letter and has_number and has_special:
                meets_criteria = True

        return password

    def possible_characters(self, include_Letters: bool, include_Numbers: bool, include_Special: bool) -> str:
        possible_characters: str = ""
        self.letters: str = string.ascii_letters * 3
        self.numbers: str = string.digits * 2
        self.special: str = r"""!"#$%&()*+-/<=>?@[\]^_{|}~"""

        if include_Letters: possible_characters += self.letters
        if include_Numbers: possible_characters += self.numbers
        if include_Special: possible_characters += self.special

        if not possible_characters: possible_characters += self.letters
        return possible_characters


def gen_aes_key(master_pass: str) -> str:
    master_key_fragment: str = get_master_key_fragment(master_pass)

    filler_lenght: int = 32 - len(master_key_fragment)
    generator: PasswordGenerator = PasswordGenerator()
    aes_key_fragment: str = generator.new_password(filler_lenght)
    aes_key: str = (master_key_fragment + aes_key_fragment)[:32]

    return aes_key, master_key_fragment, aes_key.removeprefix(master_key_fragment)


def generate_password(min_lenght: int, include_letters: bool, include_numbers: bool, include_special: bool) -> str:
    generator: PasswordGenerator = PasswordGenerator()
    password: str = generator.new_password(min_lenght, include_letters, include_numbers, include_special)

    return password


def get_master_key_fragment(master_pass: str) -> str:
    master_key_fragment_lenght: int = 15
    if len(master_pass) <= master_key_fragment_lenght:
        master_key_fragment: str = master_pass
    elif len(master_pass) >= master_key_fragment_lenght:
        master_key_fragment: str = master_pass[:master_key_fragment_lenght]

    return master_key_fragment


def get_password_lenght(minimum: int = 0) -> int:
    number: str = input("Minimale Länge des Passworts: ")
    while not number.isdigit() or int(number) < minimum:
        number: str = input(f"Bitte gib eine Zahl über {minimum} ein!: ")

    return int(number)


def gen_password_cmd() -> str:
    logging.info("Generating new passwrd")
    min_lenght: int = get_password_lenght()
    include_letters: bool = input("Soll das Passwort Buchstaben beinhalten (y/n): ").lower().replace(" ", "") == "y"
    include_numbers: bool = input("Soll das Passwort Zahlen beinhalten (y/n): ").lower().replace(" ", "") == "y"
    include_special: bool = input("Soll das Passwort Sonderzeichen beinhalten (y/n): ").lower().replace(" ", "") == "y"

    return generate_password(min_lenght, include_letters, include_numbers, include_special)
