import logging
import sys
import os

# Import GUI elements from PySide6
from PySide6.QtWidgets import (
    QVBoxLayout, QLabel, QWidget, 
    QSizePolicy, QGridLayout
)
from PySide6.QtCore import Qt


class PasswordWidget(QWidget):
    def __init__(self, styles_path: str, password_name: str, website: str, parent: QWidget | None = None):
        super(PasswordWidget, self).__init__(parent)
        logging.debug(f"Initializing: {self}")

        self.password_name: str = password_name
        self.website: str = website
        self.styles_path: str = styles_path

        self.setObjectName("PasswordCardInList")
        self.set_style_sheet()

        self.init_ui()

    def init_ui(self) -> None:
        # Main layout for the card with some margins.
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Grid layout for label/field pairs.
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(10)
        grid_layout.setVerticalSpacing(8)

        label_name = QLabel(self.password_name)
        grid_layout.addWidget(label_name, 0, 0, alignment=Qt.AlignRight)

        spacer = QLabel("")
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        grid_layout.addWidget(spacer, 0, 1)

        label_website = QLabel(self.website)
        # grid_layout.addWidget(label_website, 0, 2, alignment=Qt.AlignLeft)

        main_layout.addLayout(grid_layout)

    def set_style_sheet(self) -> None:
        css_path: str = os.path.join(self.styles_path, "list_password_widget.css")

        try:
            with open(css_path, "r") as s_f:
                self.setStyleSheet(s_f.read())
        except (FileNotFoundError, PermissionError) as e:
            logging.exception(f"Error getting style for the list_password_widget: {e}")
