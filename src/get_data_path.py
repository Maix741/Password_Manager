from pathlib import Path
import platform
import os

from .setup_folders import setup_folders


def get_data_path() -> str:
    data_path: str = get_path()

    setup_folders(data_path)

    return data_path


def get_path() -> str:
    if os.getenv("PASSWORD_MANAGER_DATA_PATH"):
        return os.getenv("PASSWORD_MANAGER_DATA_PATH")

    if platform.system() == "Windows":
        return os.path.join(os.getenv("LOCALAPPDATA"), "Password_manager")

    else:
        return os.path.join(Path.home(), ".Password_manager")
