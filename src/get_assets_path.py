from pathlib import Path
import sys
import os


def get_assets_path(data_path: str) -> str:
    path1: str = os.path.join(data_path, "assets")
    if os.path.isdir(path1):
        icons: list[str] = os.listdir(path1)
        if all([icon.endswith("-icon.png") for icon in icons]):
            return path1

    current_dir: str = os.path.dirname(sys.argv[0])
    if current_dir.endswith(("src", "bin")):
        path2: str = os.path.join(Path(current_dir).parent, "assets")
    else: path2 = os.path.join(current_dir, "assets")

    if os.path.isdir(path2):
        icons: list[str] = os.listdir(path2)
        print([icon.endswith("-icon.png") for icon in icons])
        print(icons)
        if all([icon.endswith("-icon.png") for icon in icons]):
            return path2

    print(path1, current_dir, path2)
    return ""
