import logging
import os

# Import GUI elements from PySide6
from PySide6.QtWidgets import (
    QPushButton, QVBoxLayout, QLabel, QWidget, QGridLayout,
    QSpacerItem, QSizePolicy, QHBoxLayout, QLineEdit, QFrame
)
from PySide6.QtCore import Signal, Qt, QTimer, QSize, QCoreApplication
from PySide6.QtGui import QIcon

from .load_stylesheets import load_stylesheets
from .message_box import MessageBox


class ReadPasswordWidget(QWidget):
    returned: Signal = Signal(dict)
    def __init__(self, styles_path,
                 password_name: str, password: dict[str, str],
                 assets_path: str, passwords_path: str,
                 translations_handler,
                 string_copyer,
                 parent: QWidget | None = None,
                 timer_lenght: int = 120000
                 ) -> None:
        super(ReadPasswordWidget, self).__init__(parent)

        logging.debug(f"Initializing: {self}")

        QCoreApplication.installTranslator(translations_handler.get_translator())

        self.settings_handler = parent.settings_handler

        self.copy_string = string_copyer

        self.styles_path: str = styles_path
        self.passwords_path: str = passwords_path
        self.assets_path: str = assets_path

        self.password_name: str = password_name
        self.password: dict[str, str] = password
        self.password_new: dict[str, str] = {}
        self.password_edited: bool = False

        self.setObjectName("PasswordCard")
        self.set_style_sheet()

        self.copy_icon: QIcon = QIcon(os.path.join(self.assets_path, "copy-icon.png"))
        self.show_icon: QIcon = QIcon(os.path.join(self.assets_path, "show-icon.png"))
        self.hide_icon: QIcon = QIcon(os.path.join(self.assets_path, "hide-icon.png"))
        self.back_icon: QIcon = QIcon(os.path.join(self.assets_path, "back-arrow-icon.png"))

        self.init_ui()

        # timeout in the reading window
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.return_to_list)
        self.timer.start(timer_lenght)

    def init_ui(self) -> None:
        # Main layout for the card with some margins.
        main_layout = QVBoxLayout(self)

        # Create a QFrame to act as the rounded card
        self.card_frame = QFrame(self)
        self.card_frame.setObjectName("PasswordCardFrame")
        self.card_frame.setFrameShape(QFrame.StyledPanel)
        self.card_frame.setFrameShadow(QFrame.Raised)
        card_layout = QVBoxLayout(self.card_frame)

        # Grid layout for label/field pairs
        grid_layout = QGridLayout()


        # header: back button and password name 
        header_layout: QHBoxLayout = QHBoxLayout()
        back_button: QPushButton = QPushButton(self)
        back_button.setObjectName("backButton")
        back_button.clicked.connect(self.return_to_list)
        back_button.setIcon(self.back_icon)
        back_button.setIconSize(QSize(50, 50))
        header_layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignLeft)

        label_name = QLabel(self.password_name)
        label_name.setObjectName("nameLabel")
        header_layout.addWidget(label_name, alignment=Qt.AlignmentFlag.AlignLeft)
        header_layout.addStretch()
        grid_layout.addLayout(header_layout, 0, 0, 1, 2)

        # Row 1: vertical spacing
        spacer_1 = QSpacerItem(0, 30, QSizePolicy.Minimum, QSizePolicy.Fixed)
        grid_layout.addItem(spacer_1, 1, 0, 1, 2)


        # Row 2(column 0): Username
        username_layout = QVBoxLayout()
        label_username = QLabel(self.tr("Username:"))
        username_layout.addWidget(label_username, alignment=Qt.AlignmentFlag.AlignLeft)

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText(self.tr("Username"))
        self.username_edit.setText(self.password["username"])
        self.username_edit.setReadOnly(True)

        # Create an action with the copy icon
        self.copy_username_action = self.username_edit.addAction(
            self.copy_icon, QLineEdit.TrailingPosition
        )
        self.copy_username_action.setToolTip(self.tr("copy username"))
        self.copy_username_action.triggered.connect(self.copy_username)

        username_layout.addWidget(self.username_edit)
        grid_layout.addLayout(username_layout, 2, 0)


        # Row 3(column 0): Password
        password_layout = QVBoxLayout()
        label_password = QLabel(self.tr("Password:"))
        password_layout.addWidget(label_password, alignment=Qt.AlignmentFlag.AlignLeft)

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText(self.tr("Password"))
        self.password_edit.setText(self.password["password"])
        self.password_edit.setReadOnly(True)
        self.password_edit.setEchoMode(QLineEdit.Password)

        # Create an action with the copy icon
        self.copy_password_action = self.password_edit.addAction(
            self.copy_icon, QLineEdit.TrailingPosition
        )
        self.copy_password_action.setToolTip(self.tr("copy password"))
        self.copy_password_action.triggered.connect(self.copy_password)

        # Create an action with the show icon
        self.show_password_action = self.password_edit.addAction(
            self.show_icon, QLineEdit.TrailingPosition
        )
        self.show_password_action.setToolTip(self.tr("show/hide password"))
        self.show_password_action.triggered.connect(self.hide_or_unhide_password)

        password_layout.addWidget(self.password_edit)
        grid_layout.addLayout(password_layout, 3, 0)


        # add spacers inbetween columns
        grid_layout.addItem(QSpacerItem(15, 0, QSizePolicy.Minimum, QSizePolicy.Fixed), 0, 1)
        grid_layout.addItem(QSpacerItem(15, 0, QSizePolicy.Minimum, QSizePolicy.Fixed), 1, 1)


        # Row 2(column 2): Websites
        self.website_layout = QVBoxLayout()
        label_websites = QLabel(self.tr("Websites:"))
        self.website_layout.addWidget(label_websites, alignment=Qt.AlignmentFlag.AlignLeft)

        self.add_website_label(True, False)
        grid_layout.addLayout(self.website_layout, 2, 2)

        # Row 3(column 2): Notes
        notes_layout = QVBoxLayout()
        label_note = QLabel(self.tr("Notes:"))
        notes_layout.addWidget(label_note, alignment=Qt.AlignmentFlag.AlignLeft)

        self.note_edit = QLineEdit()
        self.note_edit.setPlaceholderText(self.tr("Notes"))
        self.note_edit.setText(self.password["notes"])
        self.note_edit.setReadOnly(True)

        notes_layout.addWidget(self.note_edit)
        grid_layout.addLayout(notes_layout, 3, 2)

        # Add vertical spacing inbetween the rows
        grid_layout.addItem(QSpacerItem(0, 15, QSizePolicy.Minimum, QSizePolicy.Fixed), 2, 0, 1, 2)

        # Add vertical spacing after this row
        spacer_2 = QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        grid_layout.addItem(spacer_2, 4, 0)


        # Row 5: action buttons
        self.edit_button = QPushButton(self.tr("Edit"))
        self.edit_button.setObjectName("editButton")
        self.edit_button.clicked.connect(self.enable_editing)
        grid_layout.addWidget(self.edit_button, 5, 0, Qt.AlignmentFlag.AlignCenter)

        self.delete_button = QPushButton(self.tr("Delete"))
        self.delete_button.setObjectName("deleteButton")
        self.delete_button.clicked.connect(self.delete_password)
        grid_layout.addWidget(self.delete_button, 5, 2, Qt.AlignmentFlag.AlignCenter)

        card_layout.addLayout(grid_layout)
        card_layout.addSpacerItem(QSpacerItem(0, 30, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.card_frame.setLayout(card_layout)

        main_layout.addWidget(self.card_frame)
        self.setLayout(main_layout)

    def set_style_sheet(self) -> None:
        self.setStyleSheet(load_stylesheets(self.styles_path, "read_password_widget", self.settings_handler.get_design()))

    def hide_or_unhide_password(self) -> None:
        if self.password_edit.echoMode() != QLineEdit.Password:
            logging.debug("Hiding password")
            self.password_edit.setEchoMode(QLineEdit.Password)
            self.show_password_action.setIcon(self.show_icon)
        elif self.password_edit.echoMode() == QLineEdit.Password:
            logging.debug("Showing password")
            self.password_edit.setEchoMode(QLineEdit.Normal)
            self.show_password_action.setIcon(self.hide_icon)

    def copy_password(self) -> None:
        self.copy_string(self.password["password"], True)

    def copy_username(self) -> None:
        self.copy_string(self.password["username"], True)

    def delete_password(self) -> None:
        password_path: str = os.path.join(self.passwords_path, self.password_name)
        logging.info(f"Removing password: {self.password_name}")
        try:
            os.remove(password_path)
        except (FileNotFoundError, PermissionError) as e:
            logging.error(f"Error removing {self.password_name}: {e}")
            msg_box = MessageBox(
                self.styles_path,
                self.settings_handler,
                self
            )
            msg_box.critical(
                self.tr("Error"),
                self.tr("Could not delete password \"{password_name}\". \nPlease try again later.").format(password_name=self.password_name)
            )
        self.return_to_list()

    def add_website_label(self, type_QLabel: bool, del_previous: bool = True) -> None:
        if del_previous: self.website_label.deleteLater()
        if type_QLabel:
            self.website_label = QLabel()
            self.website_label.setText(f'''<a href='{self.password["website"]}'>{self.password["website"]}</a>''')
            self.website_label.setOpenExternalLinks(True)
        else:
            self.website_label = QLineEdit()
            self.website_label.setPlaceholderText(self.tr("Website"))
            self.website_label.setText(self.password["website"])

        self.website_layout.addWidget(self.website_label)

    def enable_editing(self) -> None:
        logging.info(f"Editing password: {self.password_name}")
        if self.password_edited:
            self.password_edited = False
            self.save_password()
            return

        self.password_edited = True

        self.username_edit.setReadOnly(False)
        self.password_edit.setReadOnly(False)
        self.note_edit.setReadOnly(False)
        self.add_website_label(False, True)

        self.edit_button.setObjectName("saveButton")
        self.set_style_sheet()
        self.edit_button.setText(self.tr("Save"))

    def save_password(self) -> None:
        logging.info(f"Saving password: {self.password_name}")
        self.username_edit.setReadOnly(True)
        self.password_edit.setReadOnly(True)
        self.note_edit.setReadOnly(True)


        self.show_password_action.setIcon(self.show_icon)
        self.edit_button.setObjectName("editButton")
        self.set_style_sheet()
        self.edit_button.setText(self.tr("Edit"))

        self.password["name"] = self.password_name
        self.password["username"] = self.username_edit.text()
        self.password["password"] = self.password_edit.text()
        self.password["website"] = self.website_label.text()
        self.password["notes"] = self.note_edit.text()

        self.add_website_label(True, True)

        if self.password_edit.echoMode() == QLineEdit.Normal:
            self.password_edit.setEchoMode(QLineEdit.Password)

        self.password_new = self.password

    def return_to_list(self) -> None:
        if self.password_new:
            self.returned.emit(self.password_new)
        else:
            self.returned.emit({})
