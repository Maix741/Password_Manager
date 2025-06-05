import logging
import os

# Import GUI elements from PySide6
from PySide6.QtWidgets import (
    QPushButton, QVBoxLayout, QLabel, QWidget, QMessageBox,
    QSpacerItem, QSizePolicy, QHBoxLayout, QLineEdit, QGridLayout
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal, Qt, QSize


class AddPasswordWidget(QWidget):
    returned: Signal = Signal(dict)
    def __init__(self, assets_path: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        logging.debug(f"Initializing: {self}")

        self.assets_path: str = assets_path
        self.password_name: str = ""
        self.password: dict[str, str] = {}

        self.setObjectName("PasswordCard")
        self.setStyleSheet("""
            QWidget#PasswordCard {
                background-color: #222233;
                border: 1px solid #000000;
                border-radius: 10px;
            }
            QLabel {
                font-size: 12pt;
                color: #BDBDBD;
            }
            QLabel#NameLabel {
                font-size: 20pt;
                color: #BDBDBD;
            }
            QLineEdit {
                border: none;
                background-color: #F9F9F9;
                padding: 5px;
                font-size: 12pt;
                color: #333333;
            }
            QPushButton {
                border: none;
                background: transparent;
                font-size: 10pt;
                color: #0078D7;
            }
            QPushButton#NameButton {
                border: none;
                background: transparent;
                font-size: 20pt;
                color: #BDBDBD;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)

        self.back_icon: QIcon = QIcon(os.path.join(self.assets_path, "back-arrow.png"))
        self.show_icon: QIcon = QIcon(os.path.join(self.assets_path, "show-icon.png"))
        self.hide_icon: QIcon = QIcon(os.path.join(self.assets_path, "hide-icon.png"))

        self.init_ui()

    def init_ui(self) -> None:
        # Main layout for the card with some margins.
        main_layout = QVBoxLayout(self)

        # Grid layout for label/field pairs
        grid_layout = QGridLayout()
        label_width = 80

        # Row 0: password name and back button
        back_button: QPushButton = QPushButton("Name:", self)
        back_button.setObjectName("NameButton")
        back_button.clicked.connect(self.return_to_list)
        back_button.setIcon(self.back_icon)
        back_button.setIconSize(QSize(50, 50))  # Adjust the size here
        grid_layout.addWidget(back_button, 0, 0, alignment=Qt.AlignLeft)


        self.name_edit = QLineEdit(self)
        grid_layout.addWidget(self.name_edit, 0, 1)


        # Add vertical spacing after this row
        spacer = QSpacerItem(0, 30, QSizePolicy.Minimum, QSizePolicy.Fixed)
        grid_layout.addItem(spacer, 1, 0, 1, 3)


        # Row 1: Username
        label_username = QLabel("Username:")
        label_username.setFixedWidth(label_width)
        grid_layout.addWidget(label_username, 2, 0, alignment=Qt.AlignRight)

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Username")
        grid_layout.addWidget(self.username_edit, 2, 1)


        # Row 2: Password
        label_password = QLabel("Password:")
        label_password.setFixedWidth(label_width)
        grid_layout.addWidget(label_password, 3, 0, alignment=Qt.AlignRight)
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Password")
        self.password_edit.setEchoMode(QLineEdit.Password)
        grid_layout.addWidget(self.password_edit, 3, 1)

        # Create an action with the show icon
        self.show_password_action = self.password_edit.addAction(
            self.show_icon, QLineEdit.TrailingPosition
        )
        self.show_password_action.setToolTip("show/hide password")
        self.show_password_action.triggered.connect(self.hide_or_unhide_password)


        # Row 3: Websites
        label_websites = QLabel("Websites:")
        label_websites.setFixedWidth(label_width)
        grid_layout.addWidget(label_websites, 4, 0, alignment=Qt.AlignRight)
        self.website_edit = QLineEdit()
        self.website_edit.setPlaceholderText("Website")

        grid_layout.addWidget(self.website_edit, 4, 1)


        # Row 4: Notes
        label_note = QLabel("Notes:")
        label_note.setFixedWidth(label_width)
        grid_layout.addWidget(label_note, 5, 0, alignment=Qt.AlignRight)
        self.note_edit = QLineEdit()
        self.note_edit.setPlaceholderText("Notes")

        grid_layout.addWidget(self.note_edit, 5, 1)

        main_layout.addLayout(grid_layout)

        # Horizontal layout for action buttons.
        button_layout = QHBoxLayout()
        button_layout.setSpacing(40)
        self.save_button = QPushButton("Save")
        button_layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_password)

        main_layout.addLayout(button_layout)

    def hide_or_unhide_password(self) -> None:
        if self.password_edit.echoMode() != QLineEdit.Password:
            logging.debug("Hiding password")
            self.password_edit.setEchoMode(QLineEdit.Password)
            self.show_password_action.setIcon(self.show_icon)
        elif self.password_edit.echoMode() == QLineEdit.Password:
            logging.debug("Showing password")
            self.password_edit.setEchoMode(QLineEdit.Normal)
            self.show_password_action.setIcon(self.hide_icon)

    def save_password(self) -> None:
        logging.info(f"Saving password: {self.password_name}")
        self.username_edit.setDisabled(True)
        self.password_edit.setDisabled(True)
        self.website_edit.setDisabled(True)
        self.note_edit.setDisabled(True)

        self.password["name"] = self.name_edit.text()
        self.password["username"] = self.username_edit.text() or "n/a"
        self.password["password"] = self.password_edit.text() or "n/a"
        self.password["website"] = self.website_edit.text() or "n/a"
        self.password["notes"] = self.note_edit.text() or "n/a"

        if self.password_edit.echoMode() == QLineEdit.Normal:
            self.password_edit.setEchoMode(QLineEdit.Password)

        if self.password["name"]:
            self.return_to_list()
        else:
            self.show_warning()

    def return_to_list(self) -> None:
        if len(self.password.values()) == 5 and self.password["name"]:
            self.returned.emit(self.password)
        else:
            self.returned.emit({})

    def show_warning(self) -> None:
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)  # Options: Information, Warning, Critical, Question
        msg_box.setWindowTitle("No name entered")
        msg_box.setText("The password needs a name to be saved!\nIf you continue it will be lost")
        yes_button = msg_box.addButton("Yes, proceed", QMessageBox.AcceptRole)
        no_button = msg_box.addButton("No, cancel", QMessageBox.RejectRole)
        msg_box.exec()

        if msg_box.clickedButton() == yes_button:
            self.return_to_list()
        elif msg_box.clickedButton() == no_button:
            return
