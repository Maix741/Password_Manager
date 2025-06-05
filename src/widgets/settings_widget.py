import logging

# Import GUI elements from PySide6
from PySide6.QtWidgets import (
    QPushButton, QVBoxLayout, QLabel, QWidget, 
    QComboBox, QHBoxLayout, QLineEdit, QGridLayout
)
from PySide6.QtCore import Signal, Qt, QTimer, QCoreApplication


class SettingsWidget(QWidget):
    returned: Signal = Signal()
    def __init__(self, settings_handler, translations_handler, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        logging.debug(f"Initializing: {self}")

        self.settings_handler = settings_handler
        self.translations_handler = translations_handler

        QCoreApplication.installTranslator(self.translations_handler.get_translator())

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
            QPushButton:hover {
                text-decoration: underline;
            }
        """)

        self.init_ui()

        # timeout in the reading window
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.return_to_list)
        self.timer.start(120000)

    def init_ui(self) -> None:
        # Main layout for the card with some margins.
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # Grid layout for label/field pairs
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(16)
        grid_layout.setVerticalSpacing(12)
        label_width = 150  # Fixed width for labels

        # row 0: data_path
        data_path_label = QLabel("Data path")
        data_path_label.setFixedWidth(label_width)
        grid_layout.addWidget(data_path_label, 0, 0, alignment=Qt.AlignRight)

        self.data_edit = QLineEdit()
        self.data_edit.setPlaceholderText("Data path")
        self.data_edit.setText(self.settings_handler.get("data_path"))
        grid_layout.addWidget(self.data_edit, 0, 1)

        # row 1: locale
        locale_label = QLabel("Locale")
        locale_label.setFixedWidth(label_width)
        grid_layout.addWidget(locale_label, 1, 0, alignment=Qt.AlignRight)

        self.locale_combo_box = QComboBox()
        self.locale_combo_box.setPlaceholderText("Locale")
        self.locale_combo_box.addItems(self.translations_handler.get_available_languages())
        self.locale_combo_box.setCurrentText(self.settings_handler.get("system_locale"))
        grid_layout.addWidget(self.locale_combo_box, 1, 1)

        # row 2: use_website_as_name
        use_website_label = QLabel("Use website as name")
        use_website_label.setFixedWidth(label_width)
        grid_layout.addWidget(use_website_label, 2, 0, alignment=Qt.AlignRight)

        self.use_website_combo_box = QComboBox()
        self.use_website_combo_box.addItems(["True", "False"])
        self.use_website_combo_box.setCurrentText(
            "True" if self.settings_handler.get("use_website_as_name") else "False"
        )
        grid_layout.addWidget(self.use_website_combo_box, 2, 1)

        # row 3: design
        design_label = QLabel("Design")
        design_label.setFixedWidth(label_width)
        grid_layout.addWidget(design_label, 3, 0, alignment=Qt.AlignRight)

        self.design_edit = QLineEdit()
        self.design_edit.setPlaceholderText("Design")
        self.design_edit.setText(str(self.settings_handler.get("design")))
        grid_layout.addWidget(self.design_edit, 3, 1)

        main_layout.addLayout(grid_layout)

        # Horizontal layout for action buttons.
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        button_layout.addStretch()
        self.save_button = QPushButton("Save")
        button_layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_settings)
        main_layout.addLayout(button_layout)

    def save_settings(self) -> None:
        logging.info("Saving settings")
        self.settings_handler.set("data_path", self.data_edit.text())
        self.settings_handler.set("system_locale", self.locale_combo_box.currentText())
        self.settings_handler.set("use_website_as_name", self.use_website_combo_box.currentText() == "True")
        self.settings_handler.set("design", self.design_edit.text())
        self.settings_handler.save()

    def return_to_list(self) -> None:
        self.returned.emit()
