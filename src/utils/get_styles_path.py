from pathlib import Path
import sys
import os


def get_styles_path(data_path: str) -> str:
    # Determine the correct path for PyInstaller
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "styles")

    path: str = os.path.join(data_path, "styles")
    if os.path.isdir(path):
        icons: list[str] = os.listdir(path)
        if all([icon.endswith(".css") for icon in icons]):
            return path

    current_dir: str = os.path.dirname(sys.argv[0])
    if current_dir.endswith("utils"):
        path_temp = str(Path(current_dir).parent)
        if path_temp.endswith(("src", "bin")):
            path: str = os.path.join(Path(path_temp).parent, "styles")
        else:
            path: str = os.path.join(path_temp, "styles")

    elif current_dir.endswith(("src", "bin")):
        path: str = os.path.join(Path(current_dir).parent, "styles")
    else: path = os.path.join(current_dir, "styles")

    if os.path.isdir(path):
        icons: list[str] = os.listdir(path)
        if all([icon.endswith(".css") for icon in icons]):
            return path

    return ""
