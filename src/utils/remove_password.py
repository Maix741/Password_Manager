import logging
import os


def remove_password(data_path: str, password_name: str) -> None:
    password_path: str = os.path.join(data_path, "passwords", f"{password_name}.json")
    logging.info(f"Removing password: {password_name}")
    try:
        os.remove(password_path)
    except (FileNotFoundError, PermissionError) as e:
        logging.error(f"Error removing {password_name}: {e}")
