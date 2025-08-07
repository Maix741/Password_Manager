# ======================================================== #
# The Password Manager as a graphical user interface (GUI) #
# ======================================================== #

from functools import partial
import logging
import os

# Import GUI elements from PySide6
from PySide6.QtWidgets import (
    QMainWindow, QPushButton, QVBoxLayout, QListWidget, QDialog,
    QMenu, QWidget, QFileDialog, QMenuBar, QListWidgetItem,
    QSpacerItem, QSizePolicy, QDockWidget, QLineEdit, QInputDialog
)
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt, QSize

# import nessesary utils
from .utils import *

# import widgets
from .widgets import *

# import constants
from .constants import *


class ManagerGUI(QMainWindow):
    def __init__(self, data_path: str | None = None, parent: QWidget | None = None) -> None:
        super(ManagerGUI, self).__init__(parent)
        self.setGeometry(*MAINWINDOW_DEFAULT_GEOMETRY)

        self.settings_handler: SettingsHandler = SettingsHandler(data_path=data_path)
        self.translation_handler: TranslationHandler = TranslationHandler(self.settings_handler)

        if data_path:
            os.makedirs(data_path, exist_ok=True)
            self.data_path = data_path
            self.settings_handler.set("data_path", data_path)
        else:
            self.data_path: str = self.settings_handler.get("data_path")
        self.update_data_path(self.data_path)

        self.password_names: list[str] = []
        self.wrong_attempts: int = 0
        self.generated_password: str = ""

        self.retry_count: int = 0
        self.max_wrong_attempts: int = MAX_WRONG_MASTER_ATTEMPTS

        self.init_ui()
        if not os.path.isfile(os.path.join(self.data_path, "master", "master_pass.pem")):
            self.renew_keys()

    def init_ui(self, create_dock: bool = True) -> None:
        """Initialize the GUI elements."""
        # Create the central widget layout
        self.setWindowTitle(self.tr("Password Manager"))
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Create a main layout for the central widget
        self.central_layout = QVBoxLayout(self.central_widget)

        self.search_edit: QLineEdit = QLineEdit(self)
        self.search_edit.setPlaceholderText(self.tr("Search passwords"))
        self.search_edit.textChanged.connect(self.on_search_text_changed)

        self.central_layout.addWidget(self.search_edit)

        self.create_passwords_list()
        self.set_style_sheet()

        if create_dock:
            self.init_icons()
            self.create_controls_dock()
            self.create_menubar()

    def set_style_sheet(self) -> None:
        self.setStyleSheet(load_stylesheets(self.styles_path, "manager_gui"))

    def reload_self(self) -> None:
        self.data_path = self.settings_handler.get("data_path")
        self.update_translations(self.settings_handler.get("system_locale"))
        self.update_data_path(self.data_path)

    def update_data_path(self, data_path: str) -> None:
        self.passwords_path = os.path.join(data_path, "passwords")
        self.assets_path = get_assets_path(data_path)
        self.styles_path = get_styles_path(data_path)
        setup_logging(os.path.join(data_path, "log", "password_manager.log"), self.settings_handler.get("log_level"))
        self.check_setup()

    def init_icons(self) -> None:
        self.icon_size: QSize = QSize(25, 25)
        self.window_icon: QIcon = QIcon(os.path.join(self.assets_path, "app-icon.png"))
        self.setWindowIcon(self.window_icon)

        self.settings_icon: QIcon = QIcon(os.path.join(self.assets_path, "settings-icon.png"))
        self.add_icon: QIcon = QIcon(os.path.join(self.assets_path, "add-icon.png"))
        self.key_icon: QIcon = QIcon(os.path.join(self.assets_path, "key-icon.png"))

        self.delete_icon: QIcon = QIcon(os.path.join(self.assets_path, "delete-icon.png"))
        self.rename_icon: QIcon = QIcon(os.path.join(self.assets_path, "rename-icon.png"))

        self.import_icon: QIcon = QIcon(os.path.join(self.assets_path, "import-icon.png"))
        self.export_icon: QIcon = QIcon(os.path.join(self.assets_path, "export-icon.png"))
        self.exit_icon: QIcon = QIcon(os.path.join(self.assets_path, "exit-icon.png"))

        self.show_icon: QIcon = QIcon(os.path.join(self.assets_path, "show-icon.png"))
        self.hide_icon: QIcon = QIcon(os.path.join(self.assets_path, "hide-icon.png"))

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
        if hasattr(self, "menubar") and self.menubar:
            self.menubar.deleteLater()
        # Create the menu bar
        self.menubar = QMenuBar(self)

        # Create "File" menu
        file_menu = QMenu(self.tr("File"), self)
        self.menubar.addMenu(file_menu)

        # Add actions to the "File" menu
        import_action = QAction(self.tr("Import"), self)
        import_action.setIcon(self.import_icon)
        import_action.triggered.connect(self.import_passwords)
        file_menu.addAction(import_action)

        export_action = QAction(self.tr("Export"), self)
        export_action.setIcon(self.export_icon)
        export_action.triggered.connect(self.export_passwords)
        file_menu.addAction(export_action)

        exit_action = QAction(self.tr("Exit"), self)
        exit_action.setIcon(self.exit_icon)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Create "Edit" menu
        edit_menu = QMenu(self.tr("Edit"), self)
        self.menubar.addMenu(edit_menu)

        # Add actions to the "Edit" menu
        settings_action = QAction(self.tr("Settings"), self)
        settings_action.setIcon(self.settings_icon)
        settings_action.triggered.connect(self.change_to_settings)

        edit_menu.addAction(settings_action)

        # Create "tools" menu
        utils_menu = QMenu(self.tr("Tools"), self)
        self.menubar.addMenu(utils_menu)

        # Add actions to the "tools" menu
        generating_action = QAction(self.tr("Generate Password"), self)
        generating_action.triggered.connect(self.show_generating_dialog)

        utils_menu.addAction(generating_action)

        check_action = QAction(self.tr("Check"), self)
        check_action.triggered.connect(self.change_to_check_card)

        utils_menu.addAction(check_action)

        self.setMenuBar(self.menubar)

    def show_password_context_menu(self, password_name: str, password_list_widget: PasswordWidget, position) -> None:
        """Show context menu for the saved playlists."""
        context_menu = QMenu(self)

        delete_action = QAction(self.tr("Delete"), self)
        delete_action.triggered.connect(partial(self.delete_password, password_name))
        delete_action.setIcon(self.delete_icon)

        context_menu.addAction(delete_action)

        rename_action = QAction(self.tr("Rename"), self)
        rename_action.triggered.connect(partial(self.rename_password, password_name))
        rename_action.setIcon(self.rename_icon)

        context_menu.addAction(rename_action)

        global_position = password_list_widget.mapToGlobal(position)
        context_menu.exec(global_position)

    def show_generating_dialog(self) -> str:
        dialog: PasswordGenerateDialog = PasswordGenerateDialog(
            self.styles_path,
            self.settings_handler, self.translation_handler,
            generate_password,
            copy_string,
            self,
            *PASSWORD_CONSTANTS
            )
        dialog.setModal(True)
        dialog.exec()
        return dialog.password_return

    def fill_passwords_list(self, passwords: list[str] | None = None) -> None:
        self.passwords_list.clear()
        if not isinstance(passwords, list):
            password_names: list[str] = os.listdir(self.passwords_path)
            self.password_names: list[str] = [password for password in password_names]
        else:
            self.password_names: list[str] = passwords

        for name in self.password_names:
            item = QListWidgetItem(self.passwords_list)
            widget = PasswordWidget(self.styles_path, name, get_website_for_password(self.passwords_path, name))
            item.setSizeHint(widget.sizeHint())
            self.passwords_list.addItem(item)
            self.passwords_list.setItemWidget(item, widget)

            # Set custom context menu
            widget.setContextMenuPolicy(Qt.CustomContextMenu)
            widget.customContextMenuRequested.connect(
                lambda pos, n=name, w=widget: self.show_password_context_menu(n, w, pos)
            )

    def create_controls_dock(self) -> None:
        """Create the dock widget with control buttons."""
        if hasattr(self, "dock_widget") and self.dock_widget:
            self.dock_widget.deleteLater()
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
        add_password_button.setObjectName("controlsDockButton")
        add_password_button.setToolTip(self.tr("Add Password"))
        add_password_button.clicked.connect(self.add_password)
        add_password_button.setIcon(self.add_icon)
        add_password_button.setIconSize(self.icon_size)
        dock_layout.addWidget(add_password_button)

        renew_keys_button: QPushButton = QPushButton(self)
        renew_keys_button.setObjectName("controlsDockButton")
        renew_keys_button.setToolTip(self.tr("Renew Keys"))
        renew_keys_button.setIcon(self.key_icon)
        renew_keys_button.setIconSize(self.icon_size)
        renew_keys_button.clicked.connect(self.change_to_key_card)
        dock_layout.addWidget(renew_keys_button)

        settings_button: QPushButton = QPushButton(self)
        settings_button.setObjectName("controlsDockButton")
        settings_button.setToolTip(self.tr("Settings"))
        settings_button.clicked.connect(self.change_to_settings)
        settings_button.setIcon(self.settings_icon)
        settings_button.setIconSize(self.icon_size)
        dock_layout.addWidget(settings_button)

        self.dock_widget.setWidget(dock_content)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_widget)

    def delete_password(self, password_name: str) -> None:
        """
        Delete a password by its name.

        Args:
            password_name (str): The name of the password to be deleted.
        """
        remove_password(self.data_path, password_name)
        self.fill_passwords_list()

    def rename_password(self, old_password_name) -> None:
        """Rename a password by its name."""
        new_password_name: str | None = self.open_input_dialog(
            self.tr("Rename Password"),
            self.tr("Enter the new password name:"),
            False
        )
        if new_password_name:
            rename_password(self.passwords_path, old_password_name, new_password_name)
            self.fill_passwords_list()

    def read_selected(self) -> None:
        current_item = self.passwords_list.currentItem()
        if current_item:
            self.read_password(self.password_names[self.passwords_list.row(current_item)])

    def read_password(self, password_name: str) -> None:
        error = None
        try:
            correct, fernet_key, AES_key = self.load_keys("read_password")
            if not correct:
                MasterWarningMessage(self).exec()
                raise Exception("Incorrect Master entered")
            logging.info(f"Reading password: {password_name}")
            reader = PasswordReader()
            decrypted_password: dict[str, str] = reader.read_password(
                name=password_name, AES_key=AES_key[0], salt=AES_key[1], fernet_key=fernet_key, password_path=self.passwords_path
            )
            password_card: ReadPasswordWidget = ReadPasswordWidget(
                styles_path=self.styles_path,
                assets_path=self.assets_path,
                passwords_path=self.passwords_path,
                password_name=password_name,
                password=decrypted_password,
                translations_handler=self.translation_handler,
                string_copyer=copy_string,
                parent=self,
                timer_lenght=INACTIVITY_TIMER_LENGHT
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
            logging.info(f"Adding Password: {password['name']}")
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
                salt=AES_key[1],
                use_website_as_name=self.settings_handler.get("use_website_as_name")
            )
            self.change_to_normal_list()

        try:
            correct, fernet_key, AES_key = self.load_keys("add_password")
            if not correct: return MasterWarningMessage(self).exec()


            password_card: AddPasswordWidget = AddPasswordWidget(self.styles_path, self.assets_path,
                                                                 self.show_generating_dialog,
                                                                 self.translation_handler,
                                                                 self
                                                                 )
            password_card.returned.connect(add_password)
            self.change_to_add_card(password_card)

        except (IndexError, PermissionError, FileNotFoundError, ValueError, KeyError) as e:
            logging.error(f"Error while adding password: {e}")
            self.retry_count += 1
            if self.retry_count <= 3:  # Retry up to 3 times
                logging.info(f"Retrying to add password (Attempt {self.retry_count}/3)...")
                self.add_password()
            else:
                logging.error("Maximum retry attempts reached. Exiting add_password process.")
                self.retry_count = 0  # Reset retry count

    def change_to_read_card(self, password_card: ReadPasswordWidget, fernet_key: bytes, AES_key: tuple[bytes]) -> None:
        def modify_password(password: dict[str, str]) -> None:
            if not password: return self.change_to_normal_list()
            logging.info(f"Modifying Password: {password['name']}")
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
        self.clear_central_layout()

        # Create a new layout for the password card
        read_card_layout = QVBoxLayout()
        read_card_layout.setAlignment(Qt.AlignTop)
        read_card_layout.addWidget(password_card)

        # Create a container widget for the layout
        self.read_card_container = QWidget(self.central_widget)
        self.read_card_container.setLayout(read_card_layout)

        # Add the container to the central layout
        self.central_layout.addWidget(self.read_card_container)
        password_card.returned.connect(modify_password)

    def clear_central_layout(self) -> None:
        # Remove all widgets from self.central_layout
        for i in reversed(range(self.central_layout.count())):
            item = self.central_layout.itemAt(i)
            widget = item.widget()
            if widget is not None:
                self.central_layout.removeWidget(widget)
                widget.deleteLater()
            else:
                # If it's a layout or spacer, remove it accordingly
                self.central_layout.removeItem(item)

    def change_to_add_card(self, add_password_card: AddPasswordWidget) -> None:
        # Clear the central layout
        self.clear_central_layout()

        # Create a new layout for the password card
        add_card_layout = QVBoxLayout()
        add_card_layout.setAlignment(Qt.AlignTop)  # Align the widget to the top
        add_card_layout.addWidget(add_password_card)

        # Create a container widget for the layout
        self.add_card_container = QWidget(self)
        self.add_card_container.setLayout(add_card_layout)

        # Add the container to the central layout
        self.central_layout.addWidget(self.add_card_container)
        if self.settings_handler.get("use_website_as_name"):
            add_password_card.name_edit.setReadOnly(True)
            add_password_card.username_edit.setFocus()
        else:
            add_password_card.name_edit.setFocus()

        add_password_card.returned.connect(self.change_to_normal_list)

    def change_to_settings(self) -> None:
        def settings_return(reload_self: bool) -> None:
            self.settings_container.deleteLater()
            del self.settings_widget
            if reload_self: self.reload_self()
            else: self.change_to_normal_list()

        # Check if settings_widget already exists and return to the list if it does
        if hasattr(self, "settings_widget") and self.settings_widget:
            logging.debug("Settings widget already exists, returning to normal list.")
            self.settings_widget.return_to_list() # FIXME: RuntimeError: Signal source has been deleted
            return

        # Clear the central layout
        self.clear_central_layout()

        # create settings widget
        self.settings_widget: SettingsWidget = SettingsWidget(self.styles_path, self.settings_handler, self.translation_handler, self)

        # Create a new layout for the settings widget
        settings_layout = QVBoxLayout()
        settings_layout.setAlignment(Qt.AlignTop)  # Align the widget to the top
        settings_layout.addWidget(self.settings_widget)

        # Create a container widget for the layout
        self.settings_container = QWidget(self)
        self.settings_container.setLayout(settings_layout)

        # Add the container to the central layout
        self.central_layout.addWidget(self.settings_container)
        self.settings_widget.returned.connect(settings_return)

    def change_to_normal_list(self) -> None:
        self.init_ui(False)

    def change_to_check_card(self) -> None:
        correct, fernet_key, AES_key  = self.load_keys("check_passwords")
        if not correct: return MasterWarningMessage(self).exec()

        # Clear the central layout
        self.clear_central_layout()

        # create check widget
        reader = PasswordReader()
        check_widget: CheckPasswordWidget = CheckPasswordWidget(
            password_reader=reader,
            fernet_key=fernet_key,
            AES_key=AES_key,
            strength_check=check_password_strength,
            duplication_check=check_password_duplication,
            styles_path=self.styles_path,
            assets_path=self.assets_path,
            passwords_path=self.passwords_path,
            translations_handler=self.translation_handler,
            constants=(PASSWORD_MIN_LENGHT, ENTROPY_THRESHOLD),
            parent=self
            )

        # Create a new layout for the password card
        check_card_layout = QVBoxLayout()
        check_card_layout.setAlignment(Qt.AlignTop)
        check_card_layout.addWidget(check_widget)

        # Create a container widget for the layout
        self.read_card_container = QWidget(self.central_widget)
        self.read_card_container.setLayout(check_card_layout)

        # Add the container to the central layout
        self.central_layout.addWidget(self.read_card_container)
        check_widget.returned.connect(self.change_to_normal_list)

    def change_to_key_card(self) -> None:
        def key_management_card_return(return_code: int) -> None:
            if return_code == 0:
                pass # do nothing
            elif return_code == 1:
                self.renew_keys_only() # renew keys without deleting passwords
            elif return_code == 2:
                self.renew_keys() # renew keys and remove passwords
            elif return_code == 3:
                delete_paswords(self.data_path) # delete passwords

            self.change_to_normal_list()
        # Clear the central layout
        self.clear_central_layout()

        # create management widget
        management_widget: KeyManagementWidget = KeyManagementWidget(
            styles_path=self.styles_path,
            assets_path=self.assets_path,
            translations_handler=self.translation_handler,
            parent=self
            )

        # Create a new layout for the password card
        management_card_layout = QVBoxLayout()
        management_card_layout.setAlignment(Qt.AlignTop)
        management_card_layout.addWidget(management_widget)

        # Create a container widget for the layout
        self.read_card_container = QWidget(self.central_widget)
        self.read_card_container.setLayout(management_card_layout)

        # Add the container to the central layout
        self.central_layout.addWidget(self.read_card_container)
        management_widget.returned.connect(key_management_card_return)

    def renew_keys(self) -> None:
        logging.info("Renewing all keys")
        new_master: str = self.ask_new_master()
        if not new_master:
            logging.info("Renewing cancelled")
            return
        renew_keys_and_delete_paswords(new_master, self.data_path)
        self.change_to_normal_list()

    def renew_keys_only(self) -> None:
        keys = self.load_keys("renew_passwords_without_deleting_passwords")
        if not keys[0]: return MasterWarningMessage(self).exec()

        logging.info("Renewing all keys without deleting passwords")
        new_master: str = self.ask_new_master()
        if not new_master:
            logging.info("Renewing cancelled")
            return

        renew_keys_only(keys, new_master, self.data_path)
        self.change_to_normal_list()

    def load_keys(self, load_from: str) -> tuple[str, bytes, list[str, bytes]] | tuple[None, None, None]:
        correct_master: str = self.ask_master_pass(load_from)
        if not correct_master:
            self.wrong_master_entered()
            return (None, None, None)

        fernet_key, AES_key_tuple = get_keys(self.data_path, correct_master)
        if not (fernet_key and AES_key_tuple):
            logging.error(f"Unable to load keys | from: {load_from}")
            self.renew_keys()
            return self.load_keys(load_from)

        return (correct_master, fernet_key, list(AES_key_tuple))

    def ask_master_pass(self, ask_from: str) -> str:
        master_pass: str | None = self.open_input_dialog(
            self.tr("Enter Master Password"),
            self.tr("Enter the master password:"),
            True
            )

        if master_pass:
            if self.validate_master_pass(master_pass, ask_from):
                return master_pass
            else:
                logging.warning("Incorrect master password was entered.")
                return ""
        else:
            logging.warning("No master password was entered.")
            return ""

    def ask_new_master(self) -> str:
        """Ask the user to set a new master password."""
        new_master: str | None = self.open_input_dialog(
            self.tr("Set New Master Password"),
            self.tr("Enter a new master password:"),
            True
        )
        if new_master:
            return new_master
        else:
            logging.warning("No master password was set.")
            return ""

    def wrong_master_entered(self) -> None:
        logging.warning("Wrong master password entered")
        self.wrong_attempts += 1
        if self.wrong_attempts >= self.max_wrong_attempts:
            logging.error("Incorrect master entered ten times!")
            self.close()

    def validate_master_pass(self, password_to_check: str, validate_from: str) -> bool:
        validator = ValidateMasterPassword(self.data_path, validate_from)
        return validator.validate(password_to_check)

    def check_setup(self) -> None:
        setup_correct: bool = check_setup(self.data_path)
        if setup_correct: logging.debug(f"Setup correct: {setup_correct}")
        elif not setup_correct: logging.warning(f"Setup correct: {setup_correct}")
        if not setup_correct: self.renew_keys()

    def import_passwords(self) -> None:
        try:
            correct, fernet_key, AES_key = self.load_keys("import_passwords")
            if not correct: return MasterWarningMessage(self).exec()

            csv_file, _ = QFileDialog.getOpenFileName(self,
                                                      self.tr("Select csv-file"),
                                                      get_download_path(),
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
            if not correct: return MasterWarningMessage(self).exec()

            csv_file, _ = QFileDialog.getSaveFileName(self,
                                                      self.tr("Save csv-file"),
                                                      os.path.join(get_download_path(), "passwords.csv"),
                                                      "csv (*.csv);;All Files (*)"
                                                    )
            if not csv_file: return

            ExportPasswords(csv_file, self.passwords_path, (fernet_key, AES_key))

        except (IndexError, PermissionError, FileNotFoundError, ValueError, KeyError) as e:
            logging.error(f"Error while exporting password: {e}")

    def update_translations(self, locale: str) -> None:
        """
        Set the language for the translation handler and reinitialize the UI,
        so that all visible UI components (menus, buttons, dialogs, etc.) are updated with the selected translations.
        """
        self.translation_handler.set_language(locale)
        self.init_ui()

    def open_input_dialog(self, title: str, label: str, password: bool = False) -> str | None:
        """Show a modal input dialog and return the typed value (or None)."""

        def show_hide_text(dialog: QInputDialog, action: QAction) -> None:
            """Toggle the visibility of the text in the line-edit."""
            if dialog.textEchoMode() == QLineEdit.Password:
                dialog.setTextEchoMode(QLineEdit.Normal)
                action.setIcon(self.hide_icon)
            else:
                dialog.setTextEchoMode(QLineEdit.Password)
                action.setIcon(self.show_icon)

        def add_show_action(dialog: QInputDialog) -> None:
            """Add a show/hide password action to the line-edit."""
            # Grab the line-edit that QInputDialog uses internally
            line_edit: QLineEdit | None = dialog.findChild(QLineEdit)
            if line_edit is None:
                return  # should never happen

            # Add the action to the trailing (right) side of the line-edit
            show_action: QAction = line_edit.addAction(
                self.show_icon, QLineEdit.TrailingPosition
            )
            show_action.setToolTip(self.tr("Show/Hide Password"))
            show_action.setCheckable(True)
            show_action.triggered.connect(partial(show_hide_text, dialog, show_action))

        dialog = QInputDialog(self)

        dialog.setWindowTitle(title)
        dialog.setLabelText(label)
        dialog.setTextValue("")                                # start with empty
        dialog.setTextEchoMode(QLineEdit.Password if password else QLineEdit.Normal)

        # styling / window flags
        dialog.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.CustomizeWindowHint
        )
        dialog.setWindowIcon(self.window_icon)
        dialog.setStyleSheet(load_stylesheets(self.styles_path, "input_dialog"))

        # If the field is a password, add the show/hide button
        if password:
            add_show_action(dialog)

        # run the dialog
        if dialog.exec_() == QDialog.Accepted:
            return dialog.textValue()
        return None
