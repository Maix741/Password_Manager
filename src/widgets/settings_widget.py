import logging
import sys
import os

# Import GUI elements from PySide6
from PySide6.QtWidgets import (
    QPushButton, QVBoxLayout, QLabel, QWidget, QSpacerItem,
    QComboBox, QHBoxLayout, QLineEdit, QGridLayout, QSizePolicy
)
from PySide6.QtCore import Signal, Qt, QCoreApplication
from PySide6.QtGui import QPainter, QBrush, QColor


class SettingsWidget(QWidget):
    returned: Signal = Signal()
    def __init__(self, styles_path: str,
                 settings_handler, translations_handler,
                 parent: QWidget | None = None
                 ) -> None:
        super(SettingsWidget, self).__init__(parent)

        logging.debug(f"Initializing: {self}")

        self.settings_handler = settings_handler
        self.translations_handler = translations_handler

        QCoreApplication.installTranslator(self.translations_handler.get_translator())

        self.design_options: list[str] = [self.tr("system"), self.tr("dark"), self.tr("light")]

        self.setObjectName("settingsWidget")
        self.set_style_sheet()

        self.init_ui()

    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setObjectName("mainLayout")
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(28)

        # Section title
        title_label = QLabel(self.tr("Settings"))
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Grid layout for label/field pairs
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(20)
        grid_layout.setVerticalSpacing(18)
        label_width = 160

        # row 0: data_path
        data_path_label = QLabel(self.tr("Data path"))
        data_path_label.setFixedWidth(label_width)
        data_path_label.setToolTip(self.tr("Location where your data is stored."))
        grid_layout.addWidget(data_path_label, 0, 0, alignment=Qt.AlignRight)

        data_path_layout = QHBoxLayout()
        self.data_edit = QLineEdit()
        self.data_edit.setPlaceholderText(self.tr("Data path"))
        self.data_edit.setReadOnly(True)
        self.data_edit.setText(self.settings_handler.get("data_path"))
        self.data_edit.setToolTip(self.tr("Location where your data is stored."))
        data_path_layout.addWidget(self.data_edit)

        browse_button = QPushButton(self.tr("Browse"))
        browse_button.setObjectName("browseButton")
        browse_button.setToolTip(self.tr("Browse for data path"))
        browse_button.clicked.connect(self.browse_data_path)
        data_path_layout.addWidget(browse_button)
        grid_layout.addLayout(data_path_layout, 0, 1)

        # row 1: locale
        locale_label = QLabel(self.tr("Locale"))
        locale_label.setFixedWidth(label_width)
        locale_label.setToolTip(self.tr("Language for the application interface."))
        grid_layout.addWidget(locale_label, 1, 0, alignment=Qt.AlignRight)

        self.locale_combo_box = QComboBox()
        self.locale_combo_box.setPlaceholderText(self.tr("Locale"))
        self.locale_combo_box.addItems(self.translations_handler.get_available_languages())
        self.locale_combo_box.setCurrentText(self.settings_handler.get("system_locale"))
        self.locale_combo_box.setToolTip(self.tr("Language for the application interface."))
        grid_layout.addWidget(self.locale_combo_box, 1, 1)

        # row 2: use_website_as_name
        use_website_label = QLabel(self.tr("Use website as name"))
        use_website_label.setFixedWidth(label_width)
        use_website_label.setToolTip(self.tr("Use the website as the entry name by default."))
        grid_layout.addWidget(use_website_label, 2, 0, alignment=Qt.AlignRight)

        self.use_website_combo_box = QComboBox()
        self.use_website_combo_box.addItems(["True", "False"])
        self.use_website_combo_box.setCurrentText(
            "True" if self.settings_handler.get("use_website_as_name") else "False"
        )
        self.use_website_combo_box.setToolTip(self.tr("Use the website as the entry name by default."))
        grid_layout.addWidget(self.use_website_combo_box, 2, 1)

        # row 3: design
        design_label = QLabel(self.tr("Design"))
        design_label.setFixedWidth(label_width)
        design_label.setToolTip(self.tr("Theme for the application."))
        grid_layout.addWidget(design_label, 3, 0, alignment=Qt.AlignRight)

        self.design_combo = QComboBox()
        self.design_combo.setPlaceholderText(self.tr("Design"))
        self.design_combo.addItems(self.design_options)
        self.design_combo.setCurrentIndex(self.settings_handler.get("design"))
        self.design_combo.setToolTip(self.tr("Theme for the application."))
        grid_layout.addWidget(self.design_combo, 3, 1)

        main_layout.addLayout(grid_layout)

        # Horizontal layout for action buttons.
        button_layout = QHBoxLayout()
        button_layout.setSpacing(30)
        button_layout.addStretch()

        self.save_button = QPushButton(self.tr("Save"))
        self.save_button.setObjectName("saveButton")
        self.save_button.setToolTip(self.tr("Save your changes"))
        button_layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_settings)

        self.cancel_button = QPushButton(self.tr("Cancel"))
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.setToolTip(self.tr("Discard changes and return"))
        self.cancel_button.clicked.connect(self.return_to_list)
        button_layout.addWidget(self.cancel_button)

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

    def browse_data_path(self):
        from PySide6.QtWidgets import QFileDialog
        path = QFileDialog.getExistingDirectory(self, self.tr("Select Data Directory"), self.data_edit.text())
        if path:
            self.data_edit.setText(path)

    def save_settings(self) -> None:
        logging.info("Saving settings")
        self.settings_handler.set("data_path", self.data_edit.text())
        self.settings_handler.set("system_locale", self.locale_combo_box.currentText())
        self.settings_handler.set("use_website_as_name", self.use_website_combo_box.currentIndex() == 0)
        self.settings_handler.set("design", self.design_combo.currentIndex())
        self.settings_handler.save()

    def return_to_list(self) -> None:
        self.returned.emit()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor("#2d2d2d")))
        painter.setPen(QColor("#000000"))
        painter.drawRoundedRect(self.rect(), 10, 10)
        super().paintEvent(event)
