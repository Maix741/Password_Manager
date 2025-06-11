import locale
import json
import os

from .get_data_path import get_data_path
from .setup_folders import setup_folders


class SettingsHandler:
    def __init__(self,
                 data_path: str = "", locale: str = locale.getlocale()[0], use_website_as_name: bool = False
                 ) -> None:

        self.tester: SettingsTester = SettingsTester()
        if data_path:
            setup_folders(data_path)
        else:
            data_path = get_data_path()

        self.settings_file: str = os.path.join(data_path, "config", "settings.json")

        # Default settings
        self.data_path: str = data_path
        self.system_locale: str = locale
        self.use_website_as_name: bool = use_website_as_name
        self.design: int = 0    # Literal[0, 1, 2] 0 -> system, 1 -> dark, 2 -> light

        self.load()

    def get(self, key: str) -> str | int | bool:
        return self.settings.get(key, None)

    def set(self, key: str, value: str | int | bool) -> None:
        self.settings[key] = value

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, "w") as file:
            json.dump(self.settings, file, indent=4)

    def load(self) -> None:
        try:
            with open(self.settings_file, "r") as file:
                self.settings: dict[str, str] = json.loads(file.read())

        except (FileNotFoundError, PermissionError, json.JSONDecodeError):
            self.settings: dict[str, str] = {}

        if self.settings:
            new_settings = self.tester.test_all_settings(self.settings)
            if new_settings != self.settings:
                self.settings = new_settings
                self.save()
            return

        self.settings: dict[str, str] = {
            "data_path": self.data_path,
            "system_locale": self.system_locale,
            "use_website_as_name": self.use_website_as_name,
            "design": self.design
        }
        self.save()


class SettingsTester:
    def __init__(self):
        self.settings: dict[str, str] = {
            "data_path": "",
            "system_locale": "en_US",
            "use_website_as_name": False,
            "design": 0
        }

    def test_all_settings(self, settings_to_test: dict[str, str | int | bool]) -> dict[str, str | int | bool]:
        try:
            if list(settings_to_test.keys()).sort() != list(self.settings.keys()).sort():
                settings_to_test = self.settings

            if not type(settings_to_test["data_path"]) == str:
                settings_to_test["data_path"] = self.settings["initial_directory"]
            if not type(settings_to_test["system_locale"]) == str:
                settings_to_test["system_locale"] = self.settings["system_locale"]
            if not type(settings_to_test["use_website_as_name"]) == bool:
                settings_to_test["use_website_as_name"] = self.settings["use_website_as_name"]
            if not type(settings_to_test["design"]) == int:
                settings_to_test["design"] = self.settings["design"]

            return settings_to_test

        except (KeyError, IndexError, ValueError): return self.settings
