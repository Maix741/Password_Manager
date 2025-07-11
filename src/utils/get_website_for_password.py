import logging
import json
import os


def get_website_for_password(passwords_path: str, password_name: str) -> str:
    try:
        password_file: str = os.path.join(passwords_path, f"{password_name}.json")
        with open(password_file, "r") as password_file_object:
            password: dict[str, str] = json.load(password_file_object)

        logging.debug(f"Got website for password: {password_name}")
        return password["website"] if password["website"] else "n/a"

    except (PermissionError, FileNotFoundError, KeyError) as exception:
        logging.error(f"Error while getting website for password ({password_name}: {exception})")
