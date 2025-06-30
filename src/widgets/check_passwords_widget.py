import logging
import os

# Import GUI elements from PySide6
from PySide6.QtWidgets import (
    QPushButton, QVBoxLayout, QLabel, QWidget, QHBoxLayout,
    QSpacerItem, QSizePolicy, QLineEdit
)
from PySide6.QtCore import Signal, Qt, QCoreApplication, QSize
from PySide6.QtGui import QPainter, QBrush, QColor, QIcon


class CheckPasswordWidget(QWidget):
    returned: Signal = Signal()
    def __init__(self,
                 password_reader, fernet_key: str, AES_key: list[bytes], strength_check, duplication_check,
                 styles_path: str, assets_path: str, passwords_path: str,
                 translations_handler,
                 parent: QWidget | None = None,
                 ) -> None:
        super(CheckPasswordWidget, self).__init__(parent)

        logging.debug(f"Initializing: {self}")

        QCoreApplication.installTranslator(translations_handler.get_translator())

        self.styles_path: str = styles_path
        self.passwords_path: str = passwords_path
        self.assets_path: str = assets_path

        self.password_reader = password_reader
        self.strenght_check = strength_check
        self.duplication_check = duplication_check

        self.setObjectName("CheckPasswordCard")
        self.set_style_sheet()

        self.list_password()
        passwords = self.decrypt_all(fernet_key, AES_key)
        self.check_passwords(passwords)

        self.init_ui()

    def init_icons(self) -> None:
        self.back_icon_size: QSize = QSize(25, 25)
        self.show_icon: QIcon = QIcon(os.path.join(self.assets_path, "show-icon.png"))
        self.hide_icon: QIcon = QIcon(os.path.join(self.assets_path, "hide-icon.png"))
        self.back_icon: QIcon = QIcon(os.path.join(self.assets_path, "back-arrow-icon.png"))

    def init_ui(self) -> None:
        self.init_icons()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header layout for back button and title
        header_layout = QHBoxLayout()
        back_btn = QPushButton(self.tr("Back"))
        back_btn.setIcon(self.back_icon)
        back_btn.setIconSize(self.back_icon_size)
        back_btn.setObjectName("BackButton")
        back_btn.clicked.connect(self.return_to_list)
        header_layout.addWidget(back_btn, alignment=Qt.AlignRight)
        layout.addLayout(header_layout)

        header_layout.addStretch()

        title = QLabel(self.tr("Password Checks"))
        title.setObjectName("CheckPasswordTitle")
        title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Weak Passwords Section
        self.weak_toggle_btn = QPushButton(
            self.tr(f"Weak Passwords (0) ▼")
        )
        self.weak_toggle_btn.setCheckable(True)
        self.weak_toggle_btn.setChecked(False)
        self.weak_toggle_btn.clicked.connect(self.toggle_weak_list)
        self.weak_toggle_btn.setObjectName("ToggleButton")
        layout.addWidget(self.weak_toggle_btn)

        self.weak_list_widget = QWidget()
        self.weak_list_layout = QVBoxLayout(self.weak_list_widget)
        self.weak_list_layout.setContentsMargins(10, 0, 0, 0)
        self.weak_list_widget.setVisible(False)
        layout.addWidget(self.weak_list_widget)

        # Reused Passwords Section
        self.reused_toggle_btn = QPushButton(
            self.tr(f"Reused Passwords (0) ▼")
        )
        self.reused_toggle_btn.setCheckable(True)
        self.reused_toggle_btn.setChecked(False)
        self.reused_toggle_btn.clicked.connect(self.toggle_reused_list)
        self.reused_toggle_btn.setObjectName("ToggleButton")
        layout.addWidget(self.reused_toggle_btn)

        self.reused_list_widget = QWidget()
        self.reused_list_layout = QVBoxLayout(self.reused_list_widget)
        self.reused_list_layout.setContentsMargins(10, 0, 0, 0)
        self.reused_list_widget.setVisible(False)
        layout.addWidget(self.reused_list_widget)

        # Spacer
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.setLayout(layout)

        # Populate the lists with password data
        self.populate_password_lists()

    def populate_password_lists(self) -> None:
        # Clear previous widgets
        for i in reversed(range(self.weak_list_layout.count())):
            widget = self.weak_list_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        for i in reversed(range(self.reused_list_layout.count())):
            widget = self.reused_list_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Add weak passwords
        for pwd in self.weak_Passwords:
            self.add_weak_password(pwd)

        count_weak = self.weak_list_layout.count()
        arrow_weak = "▼"
        if not count_weak:
            self.weak_toggle_btn.setText(self.tr(f"Weak Passwords ({count_weak}) {arrow_weak}"))
        else:
            self.weak_toggle_btn.setText(self.tr(f"⚠️ Weak Passwords ({count_weak}) {arrow_weak}"))

        # Add reused passwords
        for group in self.duplicates:
            self.add_duplicate_password(group)

        count_reused = self.reused_list_layout.count()
        arrow_reused = "▼"
        if not count_reused:
            self.reused_toggle_btn.setText(self.tr(f"Reused Passwords ({count_reused}) {arrow_reused}"))
        else:
            self.reused_toggle_btn.setText(self.tr(f"⚠️ Reused Passwords ({count_reused}) {arrow_reused}"))

    def add_weak_password(self, pwd: dict[str, str]) -> None:
        entry_widget = QWidget()
        entry_layout = QHBoxLayout(entry_widget)

        # name
        name_label = QLabel(pwd.get("name", ""))
        entry_layout.addWidget(name_label)

        # spacing
        spacer = QSpacerItem(30, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)
        entry_layout.addItem(spacer)

        # password
        password_label = QLineEdit(pwd.get("password", ""))
        password_label.setReadOnly(True)
        password_label.setEchoMode(QLineEdit.Password)
        password_label.setObjectName("PasswordLabel")
        entry_layout.addWidget(password_label)

        # actions with the show icon
        show_password_action = password_label.addAction(
            self.show_icon, QLineEdit.TrailingPosition
        )
        show_password_action.setToolTip(self.tr("show/hide password"))
        show_password_action.triggered.connect(lambda checked, label=password_label, action=show_password_action:
                                               self.toggle_password_visibility(label, action)
                                               )

        # spacing
        spacer = QLabel("")
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        entry_layout.addWidget(spacer)

        entry_widget.setObjectName("PasswordEntry")
        self.weak_list_layout.addWidget(entry_widget)

    def add_duplicate_password(self, group: list) -> None:
        # 1. Label: "x Accounts with the same password"
        group_widget = QWidget()
        group_layout = QVBoxLayout(group_widget)
        group_layout.setContentsMargins(0, 0, 0, 16)  # Add vertical spacing to next group

        count = len(group)
        group_label = QLabel(self.tr(f"{count} Accounts with the same password"))
        group_label.setObjectName("DuplicateGroupLabel")
        group_layout.addWidget(group_label)

        # 2. Each account: name, password(hidden), show_action
        for entry in group:
            entry_widget = QWidget()
            entry_layout = QHBoxLayout(entry_widget)
            entry_layout.setContentsMargins(8, 4, 8, 4)

            name_label = QLabel(entry.get("name", ""))
            name_label.setObjectName("EntryName")
            entry_layout.addWidget(name_label)

            password_label = QLineEdit(entry.get("password", ""))
            password_label.setReadOnly(True)
            password_label.setEchoMode(QLineEdit.Password)
            password_label.setObjectName("PasswordLabel")
            entry_layout.addWidget(password_label)

            show_password_action = password_label.addAction(
                self.show_icon, QLineEdit.TrailingPosition
            )
            show_password_action.setToolTip(self.tr("show/hide password"))
            show_password_action.triggered.connect(
                lambda checked=False, label=password_label, action=show_password_action:
                    self.toggle_password_visibility(label, action)
            )

            entry_layout.addStretch()

            entry_widget.setObjectName("PasswordEntry")
            group_layout.addWidget(entry_widget)

        self.reused_list_layout.addWidget(group_widget)

    def toggle_password_visibility(self, label: QLineEdit, action) -> None:
        if label.echoMode() != QLineEdit.Password:
            logging.debug("Hiding password")
            label.setEchoMode(QLineEdit.Password)
            action.setIcon(self.show_icon)
        elif label.echoMode() == QLineEdit.Password:
            logging.debug("Showing password")
            label.setEchoMode(QLineEdit.Normal)
            action.setIcon(self.hide_icon)

    def check_passwords(self, passwords: list[str]) -> None:
        self.duplicates: list[list[dict[str, str]]] = self.duplication_check(passwords)
        self.weak_Passwords = list(map(self.strenght_check, [paswd.get("password") for paswd in passwords]))
        self.weak_Passwords: list[dict[str, str]] = [x for x, y in zip(passwords, self.weak_Passwords) if not y]

    def decrypt_all(self, fernet_key, AES_key) -> None:
        passwords = []
        for password_name in self.password_names:
            password = self.password_reader.read_password(name=password_name,
                AES_key=AES_key[0], salt=AES_key[1], fernet_key=fernet_key,
                password_path=self.passwords_path
                )
            password["name"] = password_name
            passwords.append(password)
        return passwords

    def list_password(self) -> None:
        self.password_names: list[str] = [os.path.splitext(password)[0] for password in os.listdir(self.passwords_path)]

    def toggle_weak_list(self) -> None:
        count = self.weak_list_layout.count()
        if not count:
            return
        expanded = self.weak_toggle_btn.isChecked()
        self.weak_list_widget.setVisible(expanded)
        arrow = "▲" if expanded else "▼"
        self.weak_toggle_btn.setText(self.tr(f"⚠️ Weak Passwords ({count}) {arrow}"))

    def toggle_reused_list(self) -> None:
        count = self.reused_list_layout.count()
        if not count:
            return
        expanded = self.reused_toggle_btn.isChecked()
        self.reused_list_widget.setVisible(expanded)
        arrow = "▲" if expanded else "▼"
        self.reused_toggle_btn.setText(self.tr(f"⚠️ Reused Passwords ({count}) {arrow}"))

    def set_style_sheet(self) -> None:
        css_path: str = os.path.join(self.styles_path, "check_passwords_widget.css")

        try:
            with open(css_path, "r") as s_f:
                self.setStyleSheet(s_f.read())
        except (FileNotFoundError, PermissionError) as e:
            logging.exception(f"Error getting style for the check_passwords_widget: {e}")

    def return_to_list(self) -> None:
        self.returned.emit()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor("#2d2d2d")))
        painter.setPen(QColor("#000000"))
        painter.drawRoundedRect(self.rect(), 10, 10)
        super().paintEvent(event)
