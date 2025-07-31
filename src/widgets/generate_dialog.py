import logging

from PySide6.QtWidgets import (
    QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QSlider, QSpinBox, QCheckBox, QLineEdit, QSizePolicy, QGroupBox, QDialog
)
from PySide6.QtCore import Qt, QCoreApplication

from .load_stylesheets import load_stylesheets


class PasswordGenerateDialog(QDialog):
    def __init__(self, styles_path: str, settings_handler, translator, generator, password_copyer, parent=None,
                 lenght_minimum=4, lenght_maximum_spinbox=64, lenght_maximum_slider=200, lenght_start_value=12):
        super(PasswordGenerateDialog, self).__init__(parent)

        logging.debug(f"Initializing password generator (GUI): {self}")

        self.generator = generator
        self.copy_string = password_copyer

        self.settings_handler = settings_handler
        self.translator = translator

        self.styles_path: str = styles_path

        self.password: str = ""
        self.password_return: str = ""
        self.cancelled: bool = False

        self.lenght_minimum: int = lenght_minimum
        self.lenght_maximum_slider: int = lenght_maximum_slider
        self.lenght_maximum_spinbox: int = lenght_maximum_spinbox
        self.lenght_start_value: int = lenght_start_value

        QCoreApplication.installTranslator(self.translator.get_translator())

        self.set_style_sheet()

        self.init_ui()

    def init_ui(self) -> None:
        self.setWindowTitle(self.tr("Password Generator"))

        main_layout = QVBoxLayout(self)  # Set layout directly on the dialog

        # Length controls
        length_group = QGroupBox(self.tr("Password Length"))
        length_layout = QHBoxLayout()
        length_group.setLayout(length_layout)

        self.length_slider = QSlider(Qt.Horizontal)
        self.length_slider.setMinimum(self.lenght_minimum)
        self.length_slider.setMaximum(self.lenght_maximum_slider)
        self.length_slider.setValue(self.lenght_start_value)
        self.length_slider.setSingleStep(1)
        self.length_slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.lenght_spinbox = QSpinBox()
        self.lenght_spinbox.setObjectName("lenghtSpinBox")
        self.lenght_spinbox.setMinimum(self.lenght_minimum)
        self.lenght_spinbox.setMaximum(self.lenght_maximum_spinbox)
        self.lenght_spinbox.setValue(self.lenght_start_value)

        # Synchronize slider and spinbox
        self.length_slider.valueChanged.connect(self.lenght_spinbox.setValue)
        self.lenght_spinbox.valueChanged.connect(self.set_lenght_slider)

        length_layout.addWidget(QLabel(self.tr("Length:")))
        length_layout.addWidget(self.length_slider)
        length_layout.addWidget(self.lenght_spinbox)

        main_layout.addWidget(length_group)

        # Options
        options_group = QGroupBox(self.tr("Options"))
        options_layout = QVBoxLayout()
        options_group.setLayout(options_layout)

        self.letters_checkbox = QCheckBox(self.tr("Include Letters"))
        self.letters_checkbox.setChecked(True)
        self.numbers_checkbox = QCheckBox(self.tr("Include Numbers"))
        self.numbers_checkbox.setChecked(True)
        self.special_checkbox = QCheckBox(self.tr("Include Special Characters"))
        self.special_checkbox.setChecked(True)

        options_layout.addWidget(self.letters_checkbox)
        options_layout.addWidget(self.numbers_checkbox)
        options_layout.addWidget(self.special_checkbox)

        main_layout.addWidget(options_group)

        # Generated password display
        self.password_display = QLineEdit()
        self.password_display.setReadOnly(True)
        main_layout.addWidget(QLabel(self.tr("Generated Password:")))
        main_layout.addWidget(self.password_display)

        # Buttons
        button_layout = QHBoxLayout()
        self.generate_button = QPushButton(self.tr("Generate"))
        self.generate_button.setObjectName("generateButton")
        self.generate_button.clicked.connect(self.generate_password)
        self.ok_button = QPushButton(self.tr("OK"))
        self.ok_button.setObjectName("okButton")
        self.ok_button.clicked.connect(self.close)
        self.cancel_button = QPushButton(self.tr("Cancel"))
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.cancel)

        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)

    def set_style_sheet(self) -> None:
        self.setStyleSheet(load_stylesheets(self.styles_path, "generate_dialog"))

    def set_lenght_slider(self, value: int) -> None:
        if value < self.lenght_maximum_slider:
            self.length_slider.setValue(value)

    def generate_password(self) -> str:
        lenght: int = self.lenght_spinbox.value()
        include_letters: bool = self.letters_checkbox.isChecked()
        include_numbers: bool = self.numbers_checkbox.isChecked()
        include_special: bool = self.special_checkbox.isChecked()

        password: str = self.generator(
            lenght,
            include_letters,
            include_numbers,
            include_special
        )
        self.password = password
        self.password_display.setText(password)
        logging.debug("Generated password")

    def cancel(self) -> None:
        self.cancelled = True
        self.close()

    def closeEvent(self, event) -> None:
        if not self.cancelled and self.password:
            self.password_return = self.password
            self.copy_string(self.password_return, True)

        event.accept()
