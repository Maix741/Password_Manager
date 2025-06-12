from pathlib import Path
import os, sys
import platform

from .setup_folders import setup_folders


def get_data_path() -> str:
    if platform.system() == "Windows":
        data_path: str = os.path.join(os.getenv("LOCALAPPDATA"), "Password_manager")

    else:
        current_dir: str = os.path.dirname(sys.argv[0])
        if current_dir.endswith(("src", "bin")):
            data_path: str = Path(current_dir).parent
        else:
            data_path = os.path.join(current_dir, "DATA")

    setup_folders(data_path)

    return data_path
