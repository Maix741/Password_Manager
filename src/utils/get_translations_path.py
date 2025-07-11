from pathlib import Path
import os

from .get_paths import get_parent_folder


def get_translations_path(appdata_path: str = "", current_dir: str = "") -> str:
    if not (appdata_path or current_dir): appdata_path, current_dir = get_parent_folder()
    translations_folder_with_translations: str = ""

    # Get the translations folder path
    if current_dir.endswith(("src", "bin", "utils")) or ("locales" in os.listdir(current_dir)):
        translations_folder: str = os.path.join(Path(current_dir).parent, "locales")
        if "locales" in os.listdir(current_dir):
            translations_folder_with_translations: str = os.path.join(current_dir, "locales")
        if check_for_translations(translations_folder):
            translations_folder_with_translations: str = translations_folder
        else:
            translations_folder: str = os.path.join(Path(current_dir).parent.parent, "locales")
            if check_for_translations(translations_folder):
                translations_folder_with_translations: str = translations_folder

    else:
        if appdata_path:
            translations_folder: str = os.path.join(appdata_path, "Password_manager", "locales")
            if check_for_translations(translations_folder):
                translations_folder_with_translations: str = translations_folder
        else:
            translations_folder: str = os.path.join(current_dir, "locales")
            if check_for_translations(translations_folder):
                translations_folder_with_translations: str = translations_folder

    if translations_folder_with_translations:
        translations_folder: str = translations_folder_with_translations

    return translations_folder


def check_for_translations(translations_folder) -> bool:
    try:
        if [file for file in os.listdir(translations_folder) if file.endswith(".qm")]:
            return True
    except FileNotFoundError:
        return False
