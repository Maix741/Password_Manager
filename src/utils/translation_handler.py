import logging
import os

from PySide6.QtCore import QTranslator, QCoreApplication

from .get_paths import get_translations_path


LOCALE_NAMES: dict[str, str] = {
    "en_US": "English (United States)",
    "de_DE": "Deutsch (Deutschland)",
}


class TranslationHandler:
    def __init__(self, settings_handler) -> None:
        self.settings_handler = settings_handler
        self.locales_folder = get_translations_path()

        self.select_locale()

    def get_language_name(self, locale: str) -> str:
        return LOCALE_NAMES.get(locale, locale)

    def get_locale_name(self, language: str) -> str:        
        # Get the locale name from the user-friendly name
        for locale, name in LOCALE_NAMES.items():
            if name.lower() == language.lower():
                return locale
        return language

    def get_available_languages(self) -> list[str]:
        # Get the available languages from the locales folder
        try:
            return [
                self.get_language_name(filename.split(".")[0])
                for filename in os.listdir(self.locales_folder)
                if filename.endswith(".qm")
            ]
        except (FileNotFoundError, PermissionError) as e:
            logging.error(f"Unable to get available languages: {e}")
            return []

    def get_translator(self) -> QTranslator:
        return self.translator

    def select_locale(self, locale: str | None = None) -> None:
        self.locale = locale or self.settings_handler.get("system_locale")
        self.load_locale()

    def load_locale(self) -> None:
        # Load translations
        self.translator: QTranslator = QTranslator()

        translation_file: str = os.path.join(self.locales_folder, f"{self.locale}.qm")
        if self.translator.load(translation_file):
            QCoreApplication.installTranslator(self.translator)

    def set_language(self, language: str) -> None:
        # Set the language in the settings handler
        self.settings_handler.set("system_locale", language)

        # Load the new locale
        self.select_locale(language)

    def save(self) -> None:
        # Save the current locale to the settings handler
        self.settings_handler.set("system_locale", self.locale)
        self.settings_handler.save()
