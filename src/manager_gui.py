# ======================================================== #
# The Password Manager as a graphical user interface (GUI) #
# ======================================================== #

import platform
import logging
import shutil
import sys
import os

# Import GUI elements from PySide6
from PySide6.QtWidgets import (
    QMainWindow, QPushButton, QVBoxLayout, QListWidget, QMenu, QWidget, QFileDialog,
    QSpacerItem, QSizePolicy, QDockWidget, QLineEdit, QListWidgetItem, QInputDialog
)
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt, QSize

# import nessesary utils
from .generate_password import gen_aes_key, get_master_key_fragment
from .get_website_for_password import get_website_for_password
from .search_passwords import search_passwords
from .setup_logging import setup_logging
from .setup_folders import setup_folders
from .get_assets_path import get_assets_path
from .check_setup import check_setup
from .write_keys import write_keys
from .get_keys import get_keys
from .add_password import AddPassword
from .read_password import PasswordReader
from .settings_handler import SettingsHandler
from .translation_handler import TranslationHandler
from .create_master_pass import CreateMasterPassword
from .validate_master_pass import ValidateMasterPasswort
from .import_passwords import ImportPasswords
from .export_passwords import ExportPasswords

# import widgets
from .widgets import *


class ManagerGUI(QMainWindow):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setGeometry(100, 100, 1000, 600)
        self.setWindowTitle(self.tr("Password Manager"))

        self.settings_handler: SettingsHandler = SettingsHandler()
        self.translation_handler: TranslationHandler = TranslationHandler(self.settings_handler)

        self.data_path: str = self.settings_handler.get("data_path")
        self.passwords_path: str = os.path.join(self.data_path, "passwords")
        self.assets_path: str = get_assets_path(self.data_path)
        self.password_names: list[str] = []
        self.wrong_attempts: int = 0

        setup_logging(os.path.join(self.data_path, "log", "password_manager.log"))
        self.init_ui()
        if not os.path.isfile(os.path.join(self.data_path, "master", "master_pass.pem")):
            self.renew_keys()

    def init_ui(self, create_dock: bool = True) -> None:
        """Initialize the GUI elements."""
        # Create the central widget layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Create a main layout for the central widget
        self.central_layout = QVBoxLayout(self.central_widget)

        self.search_edit: QLineEdit = QLineEdit(self)
        self.search_edit.setPlaceholderText(self.tr("Search passwords"))
        self.search_edit.textChanged.connect(self.on_search_text_changed)

        self.central_layout.addWidget(self.search_edit)

        self.create_passwords_list()
        self.init_icons()

        if create_dock:
            self.create_controls_dock()
            self.create_menubar()

    def init_icons(self) -> None:
        self.icon_size: QSize = QSize(25, 25)
        self.settings_icon: QIcon = QIcon(os.path.join(self.assets_path, "settings-icon.png"))
        self.add_icon: QIcon = QIcon(os.path.join(self.assets_path, "add-icon.png"))
        self.key_icon: QIcon = QIcon(os.path.join(self.assets_path, "key-icon.png"))

    def on_search_text_changed(self, query: str) -> None:
        if not query:
            self.fill_passwords_list()
            return
        passwords = search_passwords(self.data_path, query)
        self.fill_passwords_list(passwords)

    def create_passwords_list(self) -> None:
        # create list for saved passwords
        self.passwords_list: QListWidget = QListWidget(self)
        self.passwords_list.clicked.connect(self.read_selected)
        self.central_layout.addWidget(self.passwords_list)

        self.fill_passwords_list()

    def create_menubar(self) -> None:
        """Create the menu bar with file and settings actions."""
        # Create the menu bar
        menubar = self.menuBar()

        # Create "File" menu
        file_menu = QMenu(self.tr("File"), self)
        menubar.addMenu(file_menu)

        # Add actions to the "File" menu
        import_action = QAction(self.tr("Import"), self)
        import_action.triggered.connect(self.import_passwords)
        file_menu.addAction(import_action)

        export_action = QAction(self.tr("Export"), self)
        export_action.triggered.connect(self.export_passwords)
        file_menu.addAction(export_action)

        exit_action = QAction(self.tr("Exit"), self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Create "Prefrences" menu
        preferences_menu = QMenu(self.tr("Edit"), self)
        menubar.addMenu(preferences_menu)

        # Add actions to the "Settings" menu
        settings_action = QAction(self.tr("Settings"), self)
        settings_action.triggered.connect(self.change_to_settings)


        preferences_menu.addAction(settings_action)

    def fill_passwords_list(self, passwords: list[str] | None = None) -> None:
        self.passwords_list.clear()
        if not type(passwords) == list:
            password_names: list[str] = os.listdir(self.passwords_path)
            self.password_names: list[str] = [os.path.splitext(password)[0] for password in password_names]
        elif type(passwords) == list:
            self.password_names: list[str] = passwords

        for name in self.password_names:
            item = QListWidgetItem(self.passwords_list)
            widget = PasswordWidget(name, get_website_for_password(self.passwords_path, name))
            item.setSizeHint(widget.sizeHint())
            self.passwords_list.addItem(item)
            self.passwords_list.setItemWidget(item, widget)

    def create_controls_dock(self) -> None:
        """Create the dock widget with control buttons."""
        # Create a new dock widget
        self.dock_widget = QDockWidget(self)

        self.dock_widget.setTitleBarWidget(QWidget())
        self.dock_widget.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.dock_widget.setFixedWidth(50)
        dock_content = QWidget(self)
        dock_layout = QVBoxLayout(dock_content)

        # Spacer to keep buttons at the bottom
        dock_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        add_password_button: QPushButton = QPushButton(self)
        add_password_button.setToolTip(self.tr("Add Password"))
        add_password_button.clicked.connect(self.add_password)
        add_password_button.setIcon(self.add_icon)
        add_password_button.setIconSize(self.icon_size)
        dock_layout.addWidget(add_password_button)

        renew_keys_button: QPushButton = QPushButton(self)
        renew_keys_button.setToolTip(self.tr("Renew Keys"))
        renew_keys_button.setIcon(self.key_icon)
        renew_keys_button.setIconSize(self.icon_size)
        renew_keys_button.clicked.connect(self.renew_keys)
        dock_layout.addWidget(renew_keys_button)

        settings_button: QPushButton = QPushButton(self)
        settings_button.setToolTip(self.tr("Settings"))
        settings_button.clicked.connect(self.change_to_settings)
        settings_button.setIcon(self.settings_icon)
        settings_button.setIconSize(self.icon_size)
        dock_layout.addWidget(settings_button)

        self.dock_widget.setWidget(dock_content)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_widget)

    def read_selected(self) -> None:
        current_item = self.passwords_list.currentItem()
        if current_item:
            self.read_password(self.password_names[self.passwords_list.row(current_item)])

    def read_password(self, password_name: str) -> None:
        error = None
        try:
            correct, fernet_key, AES_key = self.load_keys("read_password")
            if not correct: raise Exception
            logging.info(f"Reading password: {password_name}")
            reader = PasswordReader()
            decrypted_password: dict[str, str] = reader.read_password(
                name=password_name, AES_key=AES_key[0], salt=AES_key[1], fernet_key=fernet_key, password_path=self.passwords_path
            )
            password_card: ReadPasswordWidget = ReadPasswordWidget(password_name, decrypted_password,
                                                                   self.assets_path, self.passwords_path,
                                                                   self
                                                                   )

        except Exception as e:
            error = e
            logging.warning(f"Invalid key or name for reading: {e}")

        if not error:
            self.change_to_read_card(password_card, fernet_key, AES_key)

    def add_password(self) -> None:
        def add_password(password: dict[str, str]) -> None:
            if not len(password.keys()) == 5:
                return
            logging.info(f"Adding Password: {password["name"]}")
            AddPassword(
                name=password["name"],
                username=password["username"],
                password=password["password"],
                notes=password["notes"],
                website=password["website"],
                passwords_path=self.passwords_path,
                replace=False,
                fernet_key=fernet_key,
                AES_key=AES_key[0],
                salt=AES_key[1]
            )
            self.change_to_normal_list()

        try:
            correct, fernet_key, AES_key = self.load_keys("add_password")
            if not correct: return

            password_card: AddPasswordWidget = AddPasswordWidget(self.assets_path, self)
            password_card.returned.connect(add_password)
            self.change_to_add_card(password_card)

        except (IndexError, PermissionError, FileNotFoundError, ValueError, KeyError) as e:
            logging.error(f"Error while adding password: {e}")
            return self.add_password()

    def change_to_read_card(self, password_card: ReadPasswordWidget, fernet_key: bytes, AES_key: tuple[bytes]) -> None:
        def modify_password(password: dict[str, str]) -> None:
            if not password: return self.change_to_normal_list()
            logging.info(f"Modifying Password: {password["name"]}")
            AddPassword(
                name=password["name"],
                username=password["username"],
                password=password["password"],
                notes=password["notes"],
                website=password["website"],
                passwords_path=self.passwords_path,
                replace=True,
                fernet_key=fernet_key,
                AES_key=AES_key[0],
                salt=AES_key[1]
            )
            self.change_to_normal_list()

        # Clear the central layout
        self.central_layout.removeWidget(self.search_edit)
        self.central_layout.removeWidget(self.passwords_list)
        self.search_edit.deleteLater()
        self.passwords_list.deleteLater()

        # Create a new layout for the password card
        read_card_layout = QVBoxLayout()
        read_card_layout.setAlignment(Qt.AlignTop)  # Align the widget to the top
        read_card_layout.addWidget(password_card)

        # Create a container widget for the layout
        self.read_card_container = QWidget(self)
        self.read_card_container.setLayout(read_card_layout)

        # Add the container to the central layout
        self.central_layout.addWidget(self.read_card_container)
        password_card.returned.connect(modify_password)

    def change_to_add_card(self, password_card: AddPasswordWidget) -> None:
        # Clear the central layout
        self.central_layout.removeWidget(self.search_edit)
        self.central_layout.removeWidget(self.passwords_list)
        self.search_edit.deleteLater()
        self.passwords_list.deleteLater()

        # Create a new layout for the password card
        read_card_layout = QVBoxLayout()
        read_card_layout.setAlignment(Qt.AlignTop)  # Align the widget to the top
        read_card_layout.addWidget(password_card)

        # Create a container widget for the layout
        self.read_card_container = QWidget(self)
        self.read_card_container.setLayout(read_card_layout)

        # Add the container to the central layout
        self.central_layout.addWidget(self.read_card_container)
        password_card.returned.connect(self.change_to_normal_list)

    def change_to_settings(self) -> None:
        try:
            # Clear the central layout
            self.central_layout.removeWidget(self.search_edit)
            self.central_layout.removeWidget(self.passwords_list)
            self.search_edit.deleteLater()
            self.passwords_list.deleteLater()

        except RuntimeError:
            return self.change_to_normal_list()

        # create settings widget
        settings_widget: SettingsWidget = SettingsWidget(self.settings_handler, self.translation_handler, self)

        # Create a new layout for the settings widget
        read_card_layout = QVBoxLayout()
        read_card_layout.setAlignment(Qt.AlignTop)  # Align the widget to the top
        read_card_layout.addWidget(settings_widget)

        # Create a container widget for the layout
        self.read_card_container = QWidget(self)
        self.read_card_container.setLayout(read_card_layout)

        # Add the container to the central layout
        self.central_layout.addWidget(self.read_card_container)
        settings_widget.returned.connect(self.change_to_normal_list)

    def change_to_normal_list(self) -> None:
        self.init_ui(False)

    def renew_keys(self) -> None:
        logging.info("Renewing all keys")
        new_master: str = self.ask_new_master()
        if not new_master:
            logging.info("Renewing cancelled")
            return
        try:
            shutil.rmtree(self.passwords_path)
            shutil.rmtree(os.path.join(self.data_path, "master"))
            shutil.rmtree(os.path.join(self.data_path, "keys"))

        except (FileNotFoundError, PermissionError) as e:
            logging.error(f"Error while removing previous keys/passwords: {e}")

        setup_folders(self.data_path)
        CreateMasterPassword(self. data_path, new_master).create()

        _, _, aes_fragment = gen_aes_key(new_master)
        write_keys(self.data_path, aes_fragment)
        self.change_to_normal_list()

    def load_keys(self, load_from: str) -> tuple[str, bytes, list[str, bytes]]:
        correct_master: str = self.ask_master_pass(load_from)
        if not correct_master:
            self.wrong_master_entered()
            return (None, None, None)

        master_key_fragment: str = get_master_key_fragment(correct_master)


        fernet_key, AES_key_fragment = get_keys(self.data_path)
        if not (fernet_key and AES_key_fragment):
            logging.error(f"Unable to load keys | from: {load_from}")
            self.renew_keys()
            return self.load_keys(load_from)

        AES_key, salt = master_key_fragment + AES_key_fragment[0], AES_key_fragment[1]
        fernet_key: bytes = fernet_key

        return (correct_master, fernet_key, [AES_key, salt])

    def ask_master_pass(self, ask_from: str) -> str:
        master_pass, ok = QInputDialog.getText(
            self, 
            self.tr("Enter Master Password"), 
            self.tr("Enter the master password:"), 
            QLineEdit.Password
        )
        if ok and master_pass:
            if self.validate_master_pass(master_pass, ask_from):
                return master_pass
            else:
                logging.warning("Incorrect master password was entered.")
                return ""
        else:
            logging.warning("No master password was entered.")
            return ""

    def ask_new_master(self) -> str:
        new_master, ok = QInputDialog.getText(
            self, 
            self.tr("Set New Master Password"), 
            self.tr("Enter a new master password:"), 
            QLineEdit.Password
        )
        if ok and new_master:
            return new_master
        else:
            logging.warning("No master password was set.")
            return ""

    def wrong_master_entered(self) -> None:
        logging.warning("Wrong master password entered")
        self.wrong_attempts += 1
        if self.wrong_attempts >= 10:
            logging.error("Incorrect master entered ten times!")
            self.destroy()

    def validate_master_pass(self, password_to_check: str, validate_from: str) -> bool:
        validator = ValidateMasterPasswort(self.data_path, validate_from)
        return validator.validate(password_to_check)

    def check_setup(self) -> None:
        setup_correct: bool = check_setup(self.data_path)
        if setup_correct: logging.debug(f"Setup correct: {setup_correct}")
        elif not setup_correct: logging.warning(f"Setup correct: {setup_correct}")
        if not setup_correct: self.__init__()

    def import_passwords(self) -> None:
        try:
            correct, fernet_key, AES_key = self.load_keys("import_passwords")
            if not correct: return

            csv_file, _ = QFileDialog.getOpenFileName(self,
                                                      self.tr("Select csv-file"),
                                                      os.path.dirname(sys.argv[0]),
                                                      "csv (*.csv);;All Files (*)"
                                                    )
            if not csv_file: return

            ImportPasswords(csv_file, self.passwords_path, (fernet_key, AES_key))
            self.fill_passwords_list()

        except (IndexError, PermissionError, FileNotFoundError, ValueError, KeyError) as e:
            logging.error(f"Error while importing password: {e}")

    def export_passwords(self) -> None:
        try:
            correct, fernet_key, AES_key = self.load_keys("export_passwords")
            if not correct: return

            if platform.system() == "Windows":
                save_directory: str = os.path.join(os.environ.get("USERPROFILE", ""), "Download")
            else:
                save_directory: str = os.path.expanduser("~/Download")

            csv_file, _ = QFileDialog.getSaveFileName(self,
                                                      self.tr("Save csv-file"),
                                                      os.path.join(save_directory, "passwords.csv"),
                                                      "csv (*.csv);;All Files (*)"
                                                    )
            if not csv_file: return

            ExportPasswords(csv_file, self.passwords_path, (fernet_key, AES_key))

        except (IndexError, PermissionError, FileNotFoundError, ValueError, KeyError) as e:
            logging.error(f"Error while exporting password: {e}")
