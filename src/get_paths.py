import platform
import sys
import os


def get_parent_folder() -> tuple[str, str]:
    if platform.system() == "Windows":
        appdata_path: str = os.environ["LOCALAPPDATA"]
    elif platform.system() == "Linux":
        appdata_path: str = os.path.expanduser("~/.local/share")
    else: appdata_path = ""
    current_dir: str = os.path.dirname(sys.argv[0])

    if not (current_dir or os.path.isdir(current_dir)):
        current_dir = os.path.dirname(os.path.abspath(__file__))

    return (appdata_path, current_dir)


from .get_translations_path import get_translations_path
from .get_assets_path import get_assets_path
from .get_data_path import get_data_path
