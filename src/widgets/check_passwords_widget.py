import logging
import os

# Import GUI elements from PySide6
from PySide6.QtWidgets import (
    QPushButton, QVBoxLayout, QLabel, QWidget, QHBoxLayout,
    QSpacerItem, QSizePolicy, QLineEdit, QScrollArea
)
from PySide6.QtCore import Signal, Qt, QCoreApplication, QSize
from PySide6.QtGui import QPainter, QBrush, QColor, QIcon


class CheckPasswordWidget(QWidget):
    returned = Signal()
    def __init__(self,
                 password_reader, fernet_key: str, AES_key: list[bytes],
                 strength_check, duplication_check,
                 styles_path: str, assets_path: str, passwords_path: str,
                 translations_handler,
                 constants,
                 parent: QWidget | None = None,
                 ) -> None:
        super(CheckPasswordWidget, self).__init__(parent)

        logging.debug(f"Initializing: {self}")

        QCoreApplication.installTranslator(translations_handler.get_translator())

        self.styles_path: str = styles_path
        self.passwords_path: str = passwords_path
        self.assets_path: str = assets_path

        self.password_reader = password_reader
        self.strength_check = strength_check
        self.duplication_check = duplication_check

        self.check_constants = constants

        self.setObjectName("CheckPasswordCard")
        self.set_style_sheet()

        self.list_passwords()
        passwords: list[dict[str, str]] = self.decrypt_all(fernet_key, AES_key)
        self.check_passwords(passwords)

        self.init_ui()

    def init_icons(self) -> None:
        self.back_icon_size: QSize = QSize(25, 25)
        self.show_icon: QIcon = QIcon(os.path.join(self.assets_path, "show-icon.png"))
        self.hide_icon: QIcon = QIcon(os.path.join(self.assets_path, "hide-icon.png"))
        self.back_icon: QIcon = QIcon(os.path.join(self.assets_path, "back-arrow-icon.png"))

    def init_ui(self) -> None:
        self.init_icons()
        # Create a scroll area
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Main content widget inside the scroll area
        content_widget = QWidget()
        layout: QVBoxLayout = QVBoxLayout(content_widget)
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

        title_label: QLabel = QLabel(self.tr("Password Checks"))
        title_label.setObjectName("CheckPasswordTitle")
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header_layout.addWidget(title_label)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Weak Passwords Section
        self.weak_toggle_button: QPushButton = QPushButton(
            self.tr(f"Weak Passwords (0) ▼")
        )
        self.weak_toggle_button.setCheckable(True)
        self.weak_toggle_button.setChecked(False)
        self.weak_toggle_button.clicked.connect(self.toggle_weak_list)
        self.weak_toggle_button.setObjectName("ToggleButton")
        layout.addWidget(self.weak_toggle_button)

        self.weak_list_widget: QWidget = QWidget()
        self.weak_list_layout: QVBoxLayout = QVBoxLayout(self.weak_list_widget)
        self.weak_list_layout.setContentsMargins(10, 0, 0, 0)
        self.weak_list_widget.setVisible(False)
        layout.addWidget(self.weak_list_widget)

        # Spacer
        layout.addItem(QSpacerItem(0, 10, QSizePolicy.Fixed, QSizePolicy.Minimum))

        # Reused Passwords Section
        self.reused_toggle_button: QPushButton = QPushButton(
            self.tr(f"Reused Passwords (0) ▼")
        )
        self.reused_toggle_button.setCheckable(True)
        self.reused_toggle_button.setChecked(False)
        self.reused_toggle_button.clicked.connect(self.toggle_reused_list)
        self.reused_toggle_button.setObjectName("ToggleButton")
        layout.addWidget(self.reused_toggle_button)

        self.reused_list_widget: QWidget = QWidget()
        self.reused_list_layout: QVBoxLayout = QVBoxLayout(self.reused_list_widget)
        self.reused_list_layout.setContentsMargins(10, 0, 0, 0)
        self.reused_list_widget.setVisible(False)
        layout.addWidget(self.reused_list_widget)

        # Spacer (to continue the background until the bottom)
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Set the content widget as the scroll area's widget
        scroll_area.setWidget(content_widget)

        # Set the main layout for this widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

        # Populate the lists with password data
        self.populate_password_lists()

    def clear_lists(self) -> None:
        for i in reversed(range(self.weak_list_layout.count())):
            widget = self.weak_list_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        for i in reversed(range(self.reused_list_layout.count())):
            widget = self.reused_list_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def populate_password_lists(self) -> None:
        # Clear previous widgets
        self.clear_lists()

        # Add weak passwords
        for pwd in self.weak_passwords:
            self.add_weak_password(pwd)

        # Add reused passwords
        for group in self.duplicates:
            self.add_duplicate_password(group)

        arrow: str = "▼"

        count: int = self.weak_list_layout.count()
        if not count:
            self.weak_toggle_button.setText(self.tr("Weak Passwords ({count}) {arrow}").format(count=count, arrow=arrow))
        else:
            self.weak_toggle_button.setText(self.tr("⚠️ Weak Passwords ({count}) {arrow}").format(count=count, arrow=arrow))

        count: int = self.reused_list_layout.count()
        if not count:
            self.reused_toggle_button.setText(self.tr("Reused Passwords ({count}) {arrow}").format(count=count, arrow=arrow))
        else:
            self.reused_toggle_button.setText(self.tr("⚠️ Reused Passwords ({count}) {arrow}").format(count=count, arrow=arrow))

    def add_weak_password(self, pwd: dict[str, str]) -> None:
        entry_widget: QWidget = QWidget()
        entry_layout: QHBoxLayout = QHBoxLayout(entry_widget)

        # name
        name_label: QLabel = QLabel(pwd.get("name", ""))
        name_label.setObjectName("EntryName")
        entry_layout.addWidget(name_label)

        # spacing
        spacer: QSpacerItem = QSpacerItem(30, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)
        entry_layout.addItem(spacer)

        # password
        password_label: QLineEdit = QLineEdit(pwd.get("password", ""))
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
        spacer: QSpacerItem = QSpacerItem(30, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        entry_layout.addItem(spacer)

        entry_widget.setObjectName("PasswordEntry")
        self.weak_list_layout.addWidget(entry_widget)

    def add_duplicate_password(self, group: list[dict[str, str]]) -> None:
        # Label: "x Accounts with the same password"
        group_widget: QWidget = QWidget()
        group_layout: QVBoxLayout = QVBoxLayout(group_widget)
        group_layout.setContentsMargins(0, 0, 0, 16)  # Add vertical spacing to next group

        count: int = len(group)
        group_label: QLabel = QLabel(self.tr("{count} Accounts with the same password").format(count=count))
        group_label.setObjectName("DuplicateGroupLabel")
        group_layout.addWidget(group_label)

        # Each account: name, password(hidden) + show_action
        for entry in group:
            entry_widget: QWidget = QWidget()
            entry_layout: QHBoxLayout = QHBoxLayout(entry_widget)
            entry_layout.setContentsMargins(8, 4, 8, 4)

            name_label: QLabel = QLabel(entry.get("name", ""))
            name_label.setObjectName("EntryName")
            entry_layout.addWidget(name_label)

            password_label: QLineEdit = QLineEdit(entry.get("password", ""))
            password_label.setReadOnly(True)
            password_label.setEchoMode(QLineEdit.Password)
            password_label.setObjectName("PasswordLabel")
            entry_layout.addWidget(password_label)

            show_password_action = password_label.addAction(
                self.show_icon, QLineEdit.TrailingPosition
            )
            show_password_action.setToolTip(self.tr("show/hide password"))
            show_password_action.triggered.connect(
                lambda checked, label=password_label, action=show_password_action:
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

    def check_passwords(self, passwords: list[dict[str, str]]) -> None:
        """
        Analyze the provided list of password dictionaries to identify duplicates and weak passwords.

        Parameters:
            passwords (list[dict[str, str]]): A list of password entries, each as a dictionary with at least a "password" key.
        """
        # get reused passwords
        self.duplicates: list[list[dict[str, str]]] = self.duplication_check(passwords)

        # get weak passwords
        weak_results = [not self.strength_check(pwd.get("password"), *self.check_constants) for pwd in passwords]
        self.weak_passwords: list[dict[str, str]] = [
            pwd for pwd, is_weak in zip(passwords, weak_results) if is_weak
        ]

    def decrypt_all(self, fernet_key, AES_key) -> list[dict[str, str]]:
        passwords: list[dict[str, str]] = []
        for password_name in self.password_names:
            password = self.password_reader.read_password(name=password_name,
                AES_key=AES_key[0], salt=AES_key[1], fernet_key=fernet_key,
                password_path=self.passwords_path
                )
            password["name"] = password_name
            passwords.append(password)
        return passwords

    def list_passwords(self) -> None:
        self.password_names: list[str] = [os.path.splitext(password)[0] for password in os.listdir(self.passwords_path)]

    def toggle_weak_list(self) -> None:
        count: int = self.weak_list_layout.count()
        if not count:
            return
        expanded: bool = self.weak_toggle_button.isChecked()
        self.weak_list_widget.setVisible(expanded)
        arrow: str = "▲" if expanded else "▼"
        self.weak_toggle_button.setText(self.tr("⚠️ Weak Passwords ({count}) {arrow}").format(count=count, arrow=arrow))

    def toggle_reused_list(self) -> None:
        count: int = self.reused_list_layout.count()
        if not count:
            return
        expanded: bool = self.reused_toggle_button.isChecked()
        self.reused_list_widget.setVisible(expanded)
        arrow: str = "▲" if expanded else "▼"
        self.reused_toggle_button.setText(self.tr("⚠️ Reused Passwords ({count}) {arrow}").format(count=count, arrow=arrow))

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
        painter: QPainter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor("#2d2d2d")))
        painter.setPen(QColor("#000000"))
        painter.drawRoundedRect(self.rect(), 10, 10)
        super().paintEvent(event)
