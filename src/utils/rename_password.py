import logging
import os


def rename_password(passwords_path: str, old_name: str, new_name: str) -> bool:
    """Renames a password file from old_name to new_name in the specified passwords_path.

    Args:
        passwords_path (str): The directory where password files are stored.
        old_name (str): The current name of the password file to be renamed.
        new_name (str): new_name: The new name for the password file.

    Returns:
        bool: True if the rename was successful, False otherwise.
    """
    logging.info(f"Changing password name: \"{old_name}\" -> \"{new_name}\"")
    old_path: str = os.path.join(passwords_path, old_name)
    new_path: str = os.path.join(passwords_path, new_name)
    try:
        os.rename(old_path, new_path)
        return True
    except (PermissionError, FileNotFoundError, FileExistsError) as e:
        logging.error(f"Error renaming password \"{old_name}\": {e}")
        return False
