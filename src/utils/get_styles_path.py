from pathlib import Path
import sys
import os


def get_styles_path(data_path: str) -> str:
    # Determine the correct path for PyInstaller
    if hasattr(sys, "_MEIPASS"):
        if os.path.exists(os.path.join(sys._MEIPASS, "styles")):
            # If running from a PyInstaller bundle, return the styles path
            return os.path.join(sys._MEIPASS, "styles")

    # For development or when not using PyInstaller

    try:
        # try to use the provided data_path
        data_styles_path = os.path.join(data_path, "styles")
        if os.path.exists(data_styles_path):
            if all([f.endswith(".css") for f in os.listdir(data_styles_path)]):
                return str(data_styles_path)
    except (FileNotFoundError, PermissionError): ...

    try:
        # Fallback to the default styles directory
        current_dir = os.path.dirname(sys.argv[0])
        default_styles_path = os.path.join(Path(current_dir).parent, "styles")
        if os.path.exists(default_styles_path) and all([f.endswith(".css") for f in os.listdir(default_styles_path)]):
            return str(default_styles_path)
    except (FileNotFoundError, PermissionError): ...

    try:
        # current working directory as a last resort
        current_dir = os.path.join(os.path.dirname(sys.argv[0]), "styles")
        if os.path.exists(current_dir) and all([f.endswith(".css") for f in os.listdir(current_dir)]):
            return str(current_dir)
    except (FileNotFoundError, PermissionError): ...

    raise FileNotFoundError("Styles directory not found in any expected location.")
