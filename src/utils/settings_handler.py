from configparser import ConfigParser
from ast import literal_eval
from pathlib import Path
import logging
import locale
import os
import sys

from .get_data_path import get_data_path
from .setup_folders import setup_folders
from .is_dark_mode import is_dark_mode
from ..constants import ALL_CONSTANTS


class SettingsHandler:
    def __init__(
        self,
        data_path: str = "",
        locale: str = locale.getlocale()[0],
        use_website_as_name: bool = False,
        ) -> None:
        self.tester: SettingsTester = SettingsTester()
        self.default_constants = ALL_CONSTANTS.copy()

        if data_path:
            setup_folders(data_path)
        else:
            data_path = get_data_path()
        self.data_path: str = data_path

        self.settings_file: str = self._determine_settings_file()
        self.config = ConfigParser()
        self.settings: dict[str, str | bool | int] = {}
        self.constants: dict[str, int | tuple[int]] = {}

        self.system_locale: str = locale or locale.getlocale()[0]
        self.use_website_as_name: bool = use_website_as_name or False
        self.design: int = 0

        self.load()

    def _determine_settings_file(self) -> str:
        # 1. Check for config in data directory
        data_config = os.path.join(self.data_path, "settings.ini")
        if os.path.isfile(data_config):
            return data_config
        data_config_2 = os.path.join(self.data_path, "config", "settings.ini")
        if os.path.isfile(data_config_2):
            return data_config_2

        # 2. Compiled or not
        if getattr(sys, "frozen", False):
            # Compiled: store in same dir as exe
            return os.path.join(os.path.dirname(sys.executable), "settings.ini")
        else:
            # Not compiled: store in config folder at root
            root = os.path.dirname(sys.argv[0])
            if root.endswith("utils"): root = Path(root).parent.parent
            elif root.endswith("src"): root = Path(root).parent

            config_dir = os.path.join(root, "config")
            os.makedirs(config_dir, exist_ok=True)
            return os.path.join(config_dir, "settings.ini")

    def get(self, key: str):
        return self.settings.get(key, None)

    def get_constant(self, key: str) -> str | int | tuple:
        return self.constants.get(key.lower(), self.default_constants.get(key.lower(), None))

    def get_design(self) -> int:
        if self.settings.get("design") == 0:
            return 1 if is_dark_mode() else 2
        else:
            return self.settings.get("design", 1)

    def set(self, key: str, value):
        self.settings[key] = value

    def save(self) -> None:
        if "SETTINGS" not in self.config:
            self.config["SETTINGS"] = {}
        for k, v in self.settings.items():
            self.config.set("SETTINGS", k, str(v))

        # Save constants
        if "CONSTANTS" not in self.config:
            self.config["CONSTANTS"] = {}

        for k, v in self.constants.items():
            self.config.set("CONSTANTS", k, str(v))

        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, "w") as file:
                self.config.write(file)
        except (PermissionError, FileNotFoundError) as e:
            logging.exception(f"Error saving settings/constants to file: {e}")

    def load_constants(self) -> None:
        """Load constants from the config file, using literal_eval for safe parsing."""
        if "CONSTANTS" in self.config:
            for k, v in self.config["CONSTANTS"].items():
                try:
                    self.constants[k] = literal_eval(v)
                except (ValueError, SyntaxError):
                    self.constants[k] = v

    def set_default_settings(self) -> None:
        self.settings = {
            "data_path": self.data_path,
            "system_locale": self.system_locale,
            "use_website_as_name": self.use_website_as_name,
            "design": self.design,
            "log_level": logging.INFO
        }
        self.constants = self.default_constants
        self.save()

    def load(self) -> None:
        if not os.path.exists(self.settings_file):
            # If no settings, set defaults
            self.set_default_settings()

        self.config.read(self.settings_file)
        self.settings = dict(self.config["SETTINGS"]) if "SETTINGS" in self.config else {}
        # Convert types
        for k in self.settings:
            if k in ["use_website_as_name"]:
                self.settings[k] = self.settings[k] == "True"
            elif k in ["design", "log_level"]:
                try:
                    self.settings[k] = int(self.settings[k])
                except Exception:
                    pass
        # Load constants
        self.load_constants()

        # Validate settings
        if self.settings:
            new_settings = self.tester.test_all_settings(self.settings)
            if new_settings != self.settings:
                self.settings = new_settings
                self.save()
        else:
            self.set_default_settings()
        # Validate constants
        if self.constants:
            new_constants = self.tester.test_all_constants(self.constants)
            if new_constants != self.constants:
                self.constants = new_constants
                self.save()
        else:
            self.set_default_settings()

        self.save()


class SettingsTester:
    def __init__(self):
        self.settings: dict[str, str] = {
            "data_path": get_data_path(),
            "system_locale": "en_US",
            "use_website_as_name": False,
            "design": 0,
            "log_level": logging.INFO
        }

    def test_all_settings(self, settings_to_test: dict[str, str | int | bool]) -> dict[str, str | int | bool]:
        try:
            if sorted(settings_to_test.keys()) != sorted(self.settings.keys()):
                return self.settings

            if not isinstance(settings_to_test["data_path"], str):
                settings_to_test["data_path"] = self.settings["data_path"]
            if not isinstance(settings_to_test["system_locale"], str):
                settings_to_test["system_locale"] = self.settings["system_locale"]
            if not isinstance(settings_to_test["use_website_as_name"], bool):
                settings_to_test["use_website_as_name"] = self.settings["use_website_as_name"]
            if not isinstance(settings_to_test["design"], int):
                settings_to_test["design"] = self.settings["design"]
            if not isinstance(settings_to_test["log_level"], int):
                settings_to_test["log_level"] = self.settings["log_level"]
            return settings_to_test
        except (KeyError, IndexError, ValueError):
            return self.settings

    def test_all_constants(self, constants_to_test: dict[str, str | int | tuple]) -> dict[str, str | int | tuple]:
        try:
            if sorted(constants_to_test.keys()) != sorted(ALL_CONSTANTS.keys()):
                return ALL_CONSTANTS

            for key in ALL_CONSTANTS:
                if not isinstance(constants_to_test[key], type(ALL_CONSTANTS[key])):
                    constants_to_test[key] = ALL_CONSTANTS[key]
            return constants_to_test

        except (KeyError, IndexError, ValueError):
            return ALL_CONSTANTS
