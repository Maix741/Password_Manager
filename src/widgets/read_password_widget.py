import logging
import os

import pyperclip

# Import GUI elements from PySide6
from PySide6.QtWidgets import (
    QPushButton, QVBoxLayout, QLabel, QWidget, QGridLayout,
    QSpacerItem, QSizePolicy, QHBoxLayout, QLineEdit
)
from PySide6.QtCore import Signal, Qt, QTimer, QSize, QCoreApplication
from PySide6.QtGui import QPainter, QBrush, QColor, QIcon


class ReadPasswordWidget(QWidget):
    returned: Signal = Signal(dict)
    def __init__(self, styles_path,
                 password_name: str, password: dict[str, str],
                 assets_path: str, passwords_path: str,
                 translations_handler,
                 parent: QWidget | None = None
                 ) -> None:
        super(ReadPasswordWidget, self).__init__(parent)

        logging.debug(f"Initializing: {self}")

        QCoreApplication.installTranslator(translations_handler.get_translator())

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
        self.timer.start(120000)

    def init_ui(self) -> None:
        # Main layout for the card with some margins.
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 32, 32, 32)

        # Grid layout for label/field pairs
        grid_layout = QGridLayout()
        label_width = 80


        # Row 0: password name and back button
        back_button: QPushButton = QPushButton(self)
        back_button.setObjectName("backButton")
        back_button.clicked.connect(self.return_to_list)
        back_button.setIcon(self.back_icon)
        back_button.setIconSize(QSize(50, 50))  # Adjust the size here
        grid_layout.addWidget(back_button, 0, 0, alignment=Qt.AlignLeft)

        label_name = QLabel(self.password_name)
        # label_name.setFixedWidth(label_width)
        label_name.setObjectName("nameLabel")
        grid_layout.addWidget(label_name, 0, 1, alignment=Qt.AlignLeft)


        # Add vertical spacing after this row
        spacer = QSpacerItem(0, 30, QSizePolicy.Minimum, QSizePolicy.Fixed)
        grid_layout.addItem(spacer, 1, 0, 1, 3)


        # Row 1: Username
        label_username = QLabel(self.tr("Username:"))
        label_username.setFixedWidth(label_width)
        grid_layout.addWidget(label_username, 2, 0, alignment=Qt.AlignRight)

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

        grid_layout.addWidget(self.username_edit, 2, 1)


        # Row 2: Password
        label_password = QLabel(self.tr("Password:"))
        label_password.setFixedWidth(label_width)
        grid_layout.addWidget(label_password, 3, 0, alignment=Qt.AlignRight)

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText(self.tr("Password"))
        self.password_edit.setText(self.password["password"])
        self.password_edit.setReadOnly(True)
        self.password_edit.setEchoMode(QLineEdit.Password)
        grid_layout.addWidget(self.password_edit, 3, 1)

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


        # Row 3: Websites
        label_websites = QLabel(self.tr("Websites:"))
        label_websites.setFixedWidth(label_width)
        grid_layout.addWidget(label_websites, 4, 0, alignment=Qt.AlignRight)
        self.website_edit = QLineEdit()
        self.website_edit.setPlaceholderText(self.tr("Website"))
        self.website_edit.setText(self.password["website"])
        self.website_edit.setReadOnly(True)
        self.website_edit.setObjectName("websiteEdit")
        grid_layout.addWidget(self.website_edit, 4, 1)


        # Row 4: Notes
        label_note = QLabel(self.tr("Notes:"))
        label_note.setFixedWidth(label_width)
        grid_layout.addWidget(label_note, 5, 0, alignment=Qt.AlignRight)
        self.note_edit = QLineEdit()
        self.note_edit.setPlaceholderText(self.tr("Notes"))
        self.note_edit.setText(self.password["notes"])
        self.note_edit.setReadOnly(True)

        grid_layout.addWidget(self.note_edit, 5, 1)

        # Add vertical spacing after this row
        spacer = QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        grid_layout.addItem(spacer, 6, 0)

        main_layout.addLayout(grid_layout)


        # Horizontal layout for action buttons.
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        button_layout.addStretch()

        self.edit_button = QPushButton(self.tr("Edit"))
        self.edit_button.setObjectName("editButton")
        self.edit_button.clicked.connect(self.enable_editing)
        button_layout.addWidget(self.edit_button)

        button_layout.addStretch()

        self.delete_button = QPushButton(self.tr("Delete"))
        self.delete_button.setObjectName("deleteButton")
        self.delete_button.clicked.connect(self.delete_password)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()

        main_layout.addLayout(button_layout)

        main_layout.addSpacerItem(QSpacerItem(0, 30, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def set_style_sheet(self) -> None:
        try:
            with open(os.path.join(self.styles_path, "read_password_widget.css"), "r") as s_f:
                self.setStyleSheet(s_f.read())
        except (FileNotFoundError, PermissionError) as e:
            logging.exception(f"Error getting style for the read_password_widget: {e}")

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
        pyperclip.copy(self.password["password"])

    def copy_username(self) -> None:
        pyperclip.copy(self.password["username"])

    def delete_password(self) -> None:
        password_path: str = os.path.join(self.passwords_path, f"{self.password_name}.json")
        logging.info(f"Removing password: {self.password_name}")
        try:
            os.remove(password_path)
        except (FileNotFoundError, PermissionError) as e:
            logging.error(f"Error removing {self.password_name}: {e}")
        self.return_to_list()

    def enable_editing(self) -> None:
        logging.info(f"Editing password: {self.password_name}")
        if self.password_edited:
            self.password_edited = False
            self.save_password()
            return

        self.password_edited = True

        self.username_edit.setReadOnly(False)
        self.password_edit.setReadOnly(False)
        self.website_edit.setReadOnly(False)
        self.note_edit.setReadOnly(False)

        self.edit_button.setObjectName("saveButton")
        self.set_style_sheet()
        self.edit_button.setText("Save")

    def save_password(self) -> None:
        logging.info(f"Saving password: {self.password_name}")
        self.username_edit.setReadOnly(True)
        self.password_edit.setReadOnly(True)
        self.website_edit.setReadOnly(True)
        self.note_edit.setReadOnly(True)

        self.show_password_action.setIcon(self.show_icon)
        self.edit_button.setObjectName("editButton")
        self.set_style_sheet()
        self.edit_button.setText("Edit")

        self.password["name"] = self.password_name
        self.password["username"] = self.username_edit.text()
        self.password["password"] = self.password_edit.text()
        self.password["website"] = self.website_edit.text()
        self.password["notes"] = self.note_edit.text()

        if self.password_edit.echoMode() == QLineEdit.Normal:
            self.password_edit.setEchoMode(QLineEdit.Password)

        self.password_new = self.password

    def return_to_list(self) -> None:
        if self.password_new:
            self.returned.emit(self.password_new)
        else:
            self.returned.emit({})

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor("#2d2d2d")))
        painter.setPen(QColor("#000000"))
        painter.drawRoundedRect(self.rect(), 10, 10)
        super().paintEvent(event)
