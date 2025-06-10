import logging
import sys
import os

# Import GUI elements from PySide6
from PySide6.QtWidgets import (
    QPushButton, QVBoxLayout, QLabel, QWidget, QMessageBox,
    QSpacerItem, QSizePolicy, QHBoxLayout, QLineEdit, QGridLayout
)
from PySide6.QtCore import Signal, Qt, QSize, QCoreApplication
from PySide6.QtGui import QPainter, QBrush, QColor, QIcon


class AddPasswordWidget(QWidget):
    returned: Signal = Signal(dict)
    def __init__(self, styles_path: str, assets_path: str,
                 show_generating_dialog, translation_handler,
                 parent: QWidget | None = None
                 ) -> None:
        super(AddPasswordWidget, self).__init__(parent)

        logging.debug(f"Initializing: {self}")

        self.show_generating_dialog = show_generating_dialog

        self.assets_path: str = assets_path
        self.password_name: str = ""
        self.password: dict[str, str] = {}

        self.setObjectName("PasswordCard")
        self.set_style_sheet()

        QCoreApplication.installTranslator(translation_handler.get_translator())

        self.back_icon: QIcon = QIcon(os.path.join(self.assets_path, "back-arrow-icon.png"))
        self.show_icon: QIcon = QIcon(os.path.join(self.assets_path, "show-icon.png"))
        self.hide_icon: QIcon = QIcon(os.path.join(self.assets_path, "hide-icon.png"))
        self.back_icon_size: QSize = QSize(50, 50)

        self.init_ui()

    def init_ui(self) -> None:
        # Main layout for the card with some margins.
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 32, 32, 32)

        # Grid layout for label/field pairs
        grid_layout = QGridLayout()


        # Row 0: password name and back button
        back_button: QPushButton = QPushButton(self.tr("Name:"), self)
        back_button.setObjectName("nameButton")
        back_button.clicked.connect(self.return_to_list)
        back_button.setIcon(self.back_icon)
        back_button.setIconSize(self.back_icon_size)
        grid_layout.addWidget(back_button, 0, 0, alignment=Qt.AlignLeft)

        grid_layout.addItem(self.get_spacer(), 0, 1)

        self.name_edit = QLineEdit(self)
        grid_layout.addWidget(self.name_edit, 0, 2)


        # Add vertical spacing after this row
        spacer = QSpacerItem(0, 30, QSizePolicy.Minimum, QSizePolicy.Fixed)
        grid_layout.addItem(spacer, 1, 0, 1, 3)


        # Row 1: Username
        label_username = QLabel(self.tr("Username:"))
        grid_layout.addWidget(label_username, 2, 0, alignment=Qt.AlignRight)

        grid_layout.addItem(self.get_spacer(), 2, 1)

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText(self.tr("Username"))
        grid_layout.addWidget(self.username_edit, 2, 2)


        # Row 2: Password
        label_password = QLabel(self.tr("Password:"))
        grid_layout.addWidget(label_password, 3, 0, alignment=Qt.AlignRight)

        grid_layout.addItem(self.get_spacer(), 3, 1)

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText(self.tr("Password"))
        self.password_edit.setEchoMode(QLineEdit.Password)
        grid_layout.addWidget(self.password_edit, 3, 2)

        # Create an action with the show icon
        self.show_password_action = self.password_edit.addAction(
            self.show_icon, QLineEdit.TrailingPosition
        )
        self.show_password_action.setToolTip(self.tr("show/hide password"))
        self.show_password_action.triggered.connect(self.hide_or_unhide_password)


        # Row 3: Websites
        label_websites = QLabel(self.tr("Websites:"))
        grid_layout.addWidget(label_websites, 4, 0, alignment=Qt.AlignRight)

        grid_layout.addItem(self.get_spacer(), 4, 1)

        self.website_edit = QLineEdit()
        self.website_edit.setPlaceholderText(self.tr("Website"))

        grid_layout.addWidget(self.website_edit, 4, 2)


        # Row 4: Notes
        label_note = QLabel(self.tr("Notes:"))
        grid_layout.addWidget(label_note, 5, 0, alignment=Qt.AlignRight)

        grid_layout.addItem(self.get_spacer(), 5, 1)

        self.note_edit = QLineEdit()
        self.note_edit.setPlaceholderText(self.tr("Notes"))

        grid_layout.addWidget(self.note_edit, 5, 2)


        # Add vertical spacing after this row
        spacer = QSpacerItem(0, 15, QSizePolicy.Minimum, QSizePolicy.Fixed)
        grid_layout.addItem(spacer, 6, 0)

        main_layout.addLayout(grid_layout)


        # Horizontal layout for action buttons.
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.save_button = QPushButton(self.tr("Save"))
        self.save_button.setObjectName("saveButton")
        button_layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_password)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        main_layout.addSpacerItem(QSpacerItem(0, 30, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def set_style_sheet(self) -> None:
        # Determine the correct path for PyInstaller or normal run
        if hasattr(sys, "_MEIPASS"):
            css_path = os.path.join(sys._MEIPASS, "styles", "read_password_widget.css")
        else:
            css_path = os.path.join(self.styles_path, "read_password_widget.css")

        try:
            with open(css_path, "r") as s_f:
                self.setStyleSheet(s_f.read())
        except (FileNotFoundError, PermissionError) as e:
            logging.exception(f"Error getting style for the read_password_widget: {e}")

    def get_spacer(self) -> QSpacerItem:
        # This spacer is used to align the labels and fields in the grid layout.
        return QSpacerItem(5, 0, QSizePolicy.Minimum, QSizePolicy.Fixed)

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
        if self.password_edit.text():
            self.password["password"] = self.password_edit.text()
        else: self.password["password"] = self.show_generating_dialog()
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
        msg_box.setWindowTitle(self.tr("No name entered"))
        msg_box.setText(self.tr("The password needs a name to be saved!\nIf you continue it will be lost"))
        yes_button = msg_box.addButton(self.tr("Yes, proceed"), QMessageBox.AcceptRole)
        no_button = msg_box.addButton(self.tr("No, cancel"), QMessageBox.RejectRole)
        msg_box.exec()

        if msg_box.clickedButton() == yes_button:
            self.return_to_list()
        elif msg_box.clickedButton() == no_button:
            return

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor("#2d2d2d")))
        painter.setPen(QColor("#000000"))
        painter.drawRoundedRect(self.rect(), 10, 10)
        super().paintEvent(event)
