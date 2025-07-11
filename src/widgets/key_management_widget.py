import logging
import os

# Import GUI elements from PySide6
from PySide6.QtWidgets import (
    QPushButton, QVBoxLayout, QLabel, QWidget, QHBoxLayout,
    QSpacerItem, QSizePolicy, QLineEdit
)
from PySide6.QtCore import Signal, Qt, QCoreApplication, QSize
from PySide6.QtGui import QPainter, QBrush, QColor, QIcon


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
        layout: QVBoxLayout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header layout for back button and title
        header_layout: QHBoxLayout = QHBoxLayout()
        back_button: QPushButton = QPushButton(self.tr("Back"))

        back_button.setIcon(self.back_icon)
        back_button.setIconSize(self.back_icon_size)

        back_button.setObjectName("BackButton")
        back_button.clicked.connect(self.return_to_list)
        header_layout.addWidget(back_button, alignment=Qt.AlignRight)

        header_layout.addStretch()

        title_label: QLabel = QLabel(self.tr("Manage Keys"))
        title_label.setObjectName("KeyManagementTitle")
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header_layout.addWidget(title_label)

        header_layout.addStretch()
        layout.addLayout(header_layout)


        renew_label = QLabel(self.tr("Renew Encryption Keys"))
        renew_label.setObjectName("RenewLabel")
        renew_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(renew_label)

        renew_keep_btn = QPushButton(self.tr("Renew Keys (Keep Passwords)"))
        renew_keep_btn.setObjectName("RenewKeepButton")
        renew_keep_btn.clicked.connect(self.renew_keys_keep_passwords)
        layout.addWidget(renew_keep_btn)

        renew_delete_btn = QPushButton(self.tr("Renew Keys (Delete Passwords)"))
        renew_delete_btn.setObjectName("RenewDeleteButton")
        renew_delete_btn.clicked.connect(self.renew_keys_delete_passwords)
        layout.addWidget(renew_delete_btn)

        delete_btn = QPushButton(self.tr("Delete all Passwords"))
        delete_btn.setObjectName("DeleteButton")
        delete_btn.clicked.connect(self.delete_passwords)
        layout.addWidget(delete_btn)


        # Spacer (to continue the background until the bottom)
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.setLayout(layout)

    def renew_keys_keep_passwords(self):
        self.return_to_list(1)

    def renew_keys_delete_passwords(self):
        self.return_to_list(2)

    def delete_passwords(self) -> None:
        self.return_to_list(3)

    def set_style_sheet(self) -> None:
        css_path: str = os.path.join(self.styles_path, "key_management_widget.css")

        try:
            with open(css_path, "r") as s_f:
                self.setStyleSheet(s_f.read())
        except (FileNotFoundError, PermissionError) as e:
            logging.exception(f"Error getting style for the key_management_widget: {e}")

    def return_to_list(self, return_code: int = 0) -> None:
        self.returned.emit(return_code)

    def paintEvent(self, event):
        painter: QPainter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor("#2d2d2d")))
        painter.setPen(QColor("#000000"))
        painter.drawRoundedRect(self.rect(), 10, 10)
        super().paintEvent(event)
