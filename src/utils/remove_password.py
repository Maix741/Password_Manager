import logging
import os


def remove_password(data_path: str, password_name: str) -> bool:
    """Remove a password file from the specified data path.

    Args:
        data_path (str): The path to the data directory where passwords are stored.
        password_name (str): The name of the password file to be removed (without path).

    Returns:
        bool: True if the password was successfully removed, False otherwise.
    """
    password_path: str = os.path.join(data_path, "passwords", password_name)
    logging.info(f"Removing password: {password_name}")
    try:
        os.remove(password_path)
        return True

    except (FileNotFoundError, PermissionError) as e:
        logging.error(f"Error removing {password_name}: {e}")
        return False