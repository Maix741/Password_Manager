import platform
import os


def get_download_path() -> str:
    # Get the systems download folder path
    if platform.system() == "Windows":
        download_folder: str = os.path.join(os.environ["USERPROFILE"], "Downloads")
    elif platform.system() == "Linux":
        download_folder: str = os.path.join(os.path.expanduser("~"), "Downloads")
    else: download_folder = ""

    return download_folder


