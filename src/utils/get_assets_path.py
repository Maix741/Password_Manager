from pathlib import Path
import sys
import os


def get_assets_path(data_path: str) -> str:
    # Determine the correct path for PyInstaller
    if hasattr(sys, "_MEIPASS"):
        if os.path.exists(os.path.join(sys._MEIPASS, "assets")):
            # If running from a PyInstaller bundle, return the assets path
            return os.path.join(sys._MEIPASS, "assets")

    # For development or when not using PyInstaller

    try:
        # try to use the provided data_path
        data_assets_path = os.path.join(data_path, "assets")
        if os.path.exists(data_assets_path):
            if all([f.endswith("-icon.png") for f in os.listdir(data_assets_path)]):
                return str(data_assets_path)
    except (FileNotFoundError, PermissionError): ...

    try:
        # Fallback to the default assets directory
        current_dir = os.path.dirname(sys.argv[0])
        default_assets_path = os.path.join(Path(current_dir).parent, "assets")
        if os.path.exists(default_assets_path) and all([f.endswith("-icon.png") for f in os.listdir(default_assets_path)]):
            return str(default_assets_path)
    except (FileNotFoundError, PermissionError): ...

    try:
        # current working directory as a last resort
        current_dir = os.path.join(os.path.dirname(sys.argv[0]), "assets")
        if os.path.exists(current_dir) and all([f.endswith("-icon.png") for f in os.listdir(current_dir)]):
            return str(current_dir)
    except (FileNotFoundError, PermissionError): ...

    raise FileNotFoundError("Assets directory not found in any expected location.")
