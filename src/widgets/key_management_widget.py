import logging
import os

# Import GUI elements from PySide6
from PySide6.QtWidgets import (
    QPushButton, QVBoxLayout, QLabel, QHBoxLayout,
    QSpacerItem, QSizePolicy, QFrame, QWidget
)
from PySide6.QtCore import Signal, Qt, QCoreApplication, QSize
from PySide6.QtGui import QIcon

from .load_stylesheets import load_stylesheets


class KeyManagementWidget(QWidget):
    returned: Signal = Signal(int)
    def __init__(self,
                 styles_path: str, assets_path: str,
                 translations_handler,
                 parent: QWidget | None = None,
                 ) -> None:
        super(KeyManagementWidget, self).__init__(parent)

        logging.debug(f"Initializing: {self}")

        QCoreApplication.installTranslator(translations_handler.get_translator())

        self.settings_handler = parent.settings_handler

        self.styles_path: str = styles_path
        self.assets_path: str = assets_path

        self.setObjectName("KeyManagementWidget")
        self.set_style_sheet()

        self.init_ui()

    def init_icons(self) -> None:
        self.back_icon_size: QSize = QSize(25, 25)
        self.show_icon: QIcon = QIcon(os.path.join(self.assets_path, "show-icon.png"))
        self.hide_icon: QIcon = QIcon(os.path.join(self.assets_path, "hide-icon.png"))
        self.back_icon: QIcon = QIcon(os.path.join(self.assets_path, "back-arrow-icon.png"))

    def init_ui(self) -> None:
        self.init_icons()
        main_layout: QVBoxLayout = QVBoxLayout(self)

        # Create a QFrame to act as the rounded card
        self.card_frame = QFrame(self)
        self.card_frame.setObjectName("PasswordCardFrame")
        self.card_frame.setFrameShape(QFrame.StyledPanel)
        self.card_frame.setFrameShadow(QFrame.Raised)
        card_layout = QVBoxLayout(self.card_frame)

        content_layout: QVBoxLayout = QVBoxLayout()
        content_layout.setSpacing(15)

        # Header layout for back button and title
        header_layout: QHBoxLayout = QHBoxLayout()
        back_button: QPushButton = QPushButton(self.tr("Back"))

        back_button.setIcon(self.back_icon)
        back_button.setIconSize(self.back_icon_size)

        back_button.setObjectName("BackButton")
        back_button.clicked.connect(self.return_to_list)
        header_layout.addWidget(back_button, alignment=Qt.AlignRight)

        header_layout.addStretch()

        title_label: QLabel = QLabel(self.tr("Manage encryption Keys"))
        title_label.setObjectName("KeyManagementTitle")
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header_layout.addWidget(title_label)

        header_layout.addStretch()
        content_layout.addLayout(header_layout)


        renew_label = QLabel(self.tr("Renew Encryption Keys"))
        renew_label.setObjectName("RenewLabel")
        renew_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        content_layout.addWidget(renew_label)

        renew_keep_btn = QPushButton(self.tr("Renew Keys (Keep Passwords)"))
        renew_keep_btn.setObjectName("RenewKeepButton")
        renew_keep_btn.clicked.connect(self.renew_keys_keep_passwords)
        content_layout.addWidget(renew_keep_btn)

        renew_delete_btn = QPushButton(self.tr("Renew Keys (Delete Passwords)"))
        renew_delete_btn.setObjectName("RenewDeleteButton")
        renew_delete_btn.clicked.connect(self.renew_keys_delete_passwords)
        content_layout.addWidget(renew_delete_btn)

        delete_btn = QPushButton(self.tr("Delete all Passwords"))
        delete_btn.setObjectName("DeleteButton")
        delete_btn.clicked.connect(self.delete_passwords)
        content_layout.addWidget(delete_btn)


        # Spacer (to continue the background until the bottom)
        content_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        card_layout.addLayout(content_layout)
        self.card_frame.setLayout(card_layout)

        main_layout.addWidget(self.card_frame)
        self.setLayout(main_layout)

    def renew_keys_keep_passwords(self):
        self.return_to_list(1)

    def renew_keys_delete_passwords(self):
        self.return_to_list(2)

    def delete_passwords(self) -> None:
        self.return_to_list(3)

    def set_style_sheet(self) -> None:
        self.setStyleSheet(load_stylesheets(self.styles_path, "key_management_widget", self.settings_handler.get_design()))

    def return_to_list(self, return_code: int = 0) -> None:
        self.returned.emit(return_code)
