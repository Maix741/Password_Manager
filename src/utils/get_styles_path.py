from pathlib import Path
import sys
import os


def get_styles_path(data_path: str) -> str:
    # Determine the correct path for PyInstaller
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "styles")

    path1: str = os.path.join(data_path, "styles")
    if os.path.isdir(path1):
        icons: list[str] = os.listdir(path1)
        if all([icon.endswith(".css") for icon in icons]):
            return path1

    current_dir: str = os.path.dirname(sys.argv[0])
    if current_dir.endswith(("src", "bin")):
        path2: str = os.path.join(Path(current_dir).parent, "styles")
    else: path2 = os.path.join(current_dir, "styles")

    if os.path.isdir(path2):
        icons: list[str] = os.listdir(path2)
        if all([icon.endswith(".css") for icon in icons]):
            return path2

    return ""
