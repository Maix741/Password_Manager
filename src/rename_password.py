import logging
import os


def rename_password(passwords_path: str, old_name: str, new_name: str) -> None:
    logging.info(f"Changing password name: \"{old_name}\" -> \"{new_name}\"")
    old_path: str = os.path.join(passwords_path, f"{old_name}.json")
    new_path: str = os.path.join(passwords_path, f"{new_name}.json")
    try:
        os.rename(old_path, new_path)

    except (PermissionError, FileNotFoundError, FileExistsError) as e:
        logging.error(f"Error renaming password \"{old_name}\": {e}")
