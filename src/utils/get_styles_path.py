from pathlib import Path
import sys
import os


def get_styles_path(data_path: str) -> str:
    # Determine the correct path for PyInstaller
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "styles")

    # For development or when not using PyInstaller

    # try to use the provided data_path
    data_styles_path = os.path.join(data_path, "styles")
    if os.path.exists(data_styles_path):
        if ["dark", "light"] == os.listdir(data_styles_path):
            return str(data_styles_path)

    # Fallback to the default styles directory
    current_dir = os.path.dirname(sys.argv[0])
    default_styles_path = os.path.join(Path(current_dir).parent, "styles")
    if os.path.exists(default_styles_path) and (["dark", "light"] == os.listdir(data_styles_path)):
        return str(default_styles_path)

    # current working directory as a last resort
    current_dir = os.path.join(os.path.dirname(sys.argv[0]), "styles")
    if os.path.exists(current_dir) and (["dark", "light"] == os.listdir(current_dir)):
        return str(current_dir)

    raise FileNotFoundError("Styles directory not found in any expected location.")
