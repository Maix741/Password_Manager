import logging

from PySide6.QtWidgets import (
    QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QSlider, QSpinBox, QCheckBox, QLineEdit, QSizePolicy, QGroupBox, QDialog
)
from PySide6.QtCore import Qt, QCoreApplication
import pyperclip


class PasswordGenerateDialog(QDialog):
    def __init__(self, settings_handler, translator, generator, parent=None):
        super(PasswordGenerateDialog, self).__init__(parent)

        logging.debug("Password generator (GUI) initialized")

        self.generator = generator
        self.settings_handler = settings_handler
        self.translator = translator

        self.password: str = ""
        self.password_return: str = ""
        self.cancelled: bool = False

        self.lenght_minimum: int = 4
        self.lenght_maximum: int = 64
        self.lenght_start_value: int = 12

        QCoreApplication.installTranslator(self.translator.get_translator())

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
        self.length_slider.setMaximum(self.lenght_maximum)
        self.length_slider.setValue(self.lenght_start_value)
        self.length_slider.setTickInterval(1)
        self.length_slider.setTickPosition(QSlider.TicksBelow)
        self.length_slider.setSingleStep(1)
        self.length_slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.length_spinbox = QSpinBox()
        self.length_spinbox.setMinimum(self.lenght_minimum)
        self.length_spinbox.setMaximum(self.lenght_maximum)
        self.length_spinbox.setValue(self.lenght_start_value)

        # Synchronize slider and spinbox
        self.length_slider.valueChanged.connect(self.length_spinbox.setValue)
        self.length_spinbox.valueChanged.connect(self.length_slider.setValue)

        length_layout.addWidget(QLabel(self.tr("Length:")))
        length_layout.addWidget(self.length_slider)
        length_layout.addWidget(self.length_spinbox)

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
        self.generate_button.clicked.connect(self.generate_password)
        self.ok_button = QPushButton(self.tr("OK"))
        self.ok_button.clicked.connect(self.close)
        self.cancel_button = QPushButton(self.tr("Cancel"))
        self.cancel_button.clicked.connect(self.cancel)

        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)

    def generate_password(self) -> str:
        lenght: int = self.length_slider.value()
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
            pyperclip.copy(self.password_return)

        event.accept()
