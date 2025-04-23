import logging

# Import GUI elements from PySide6
from PySide6.QtWidgets import (
    QVBoxLayout, QLabel, QWidget, 
    QSizePolicy, QGridLayout
)
from PySide6.QtCore import Qt


class PasswordWidget(QWidget):
    def __init__(self, password_name: str, website: str, parent: QWidget | None = None):
        super().__init__(parent)
        logging.debug(f"Initializing: {self}")

        self.password_name: str = password_name
        self.website: str = website
    
        self.setObjectName("PasswordCardInList")
        self.setStyleSheet("""
            QWidget#PasswordCardInList {
                background-color: #222233;
                border: 1px solid #000000;
                border-radius: 10px;
            }
            QLabel {
                font-size: 12pt;
                color: #BDBDBD;
            }
            QPushButton {
                border: none;
                background: transparent;
                font-size: 10pt;
                color: #0078D7;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)

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
