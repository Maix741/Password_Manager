from pathlib import Path
import platform
import logging
import os

from .setup_folders import setup_folders


def get_data_path() -> str:
    data_path: str = get_path()

    try:
        setup_folders(data_path)
    except (FileNotFoundError, PermissionError) as e:
        logging.error(f"\"{data_path}\" could not be used because of: {e}")
        data_path: str = custom_path_not_available()
        setup_folders(data_path)
    return data_path


def get_path() -> str:
    if os.getenv("PASSWORD_MANAGER_DATA_PATH"):
        return os.getenv("PASSWORD_MANAGER_DATA_PATH")

    if platform.system() == "Windows":
        return os.path.join(os.getenv("LOCALAPPDATA"), "Password_manager")

    else:
        return os.path.join(Path.home(), ".Password_manager")


def custom_path_not_available() -> str:
    if platform.system() == "Windows":
        return os.path.join(os.getenv("LOCALAPPDATA"), "Password_manager")

    else:
        return os.path.join(Path.home(), ".Password_manager")
