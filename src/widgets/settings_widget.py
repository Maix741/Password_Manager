import logging

# Import GUI elements from PySide6
from PySide6.QtWidgets import (
    QPushButton, QVBoxLayout, QLabel, QWidget, QSpacerItem, QFrame,
    QComboBox, QHBoxLayout, QLineEdit, QGridLayout, QSizePolicy, QFileDialog
)
from PySide6.QtCore import Signal, Qt, QCoreApplication

from .load_stylesheets import load_stylesheets


class SettingsWidget(QWidget):
    returned: Signal = Signal(bool)
    def __init__(self, styles_path: str,
                 settings_handler, translations_handler,
                 parent: QWidget | None = None
                 ) -> None:
        super(SettingsWidget, self).__init__(parent)

        logging.debug(f"Initializing: {self}")

        self.settings_handler = settings_handler
        self.translations_handler = translations_handler

        self.styles_path: str = styles_path

        QCoreApplication.installTranslator(self.translations_handler.get_translator())

        self.design_options: list[str] = [self.tr("system"), self.tr("dark"), self.tr("light")]

        self.data_path_changed: bool = False
        self.language_changed: bool = False

        self.setObjectName("settingsWidget")
        self.set_style_sheet()

        self.init_ui()

    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(28)

        # Create a QFrame to act as the rounded card
        self.card_frame = QFrame(self)
        self.card_frame.setObjectName("PasswordCardFrame")
        self.card_frame.setFrameShape(QFrame.StyledPanel)
        self.card_frame.setFrameShadow(QFrame.Raised)
        card_layout = QVBoxLayout(self.card_frame)

        # Section title
        title_label = QLabel(self.tr("Settings"))
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title_label)

        # Spacer between title and widget
        card_layout.addSpacerItem(QSpacerItem(0, 30, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Grid layout for label/field pairs
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(20)
        grid_layout.setVerticalSpacing(18)

        # row 0: data_path
        data_path_label = QLabel(self.tr("Data path"))
        data_path_label.setToolTip(self.tr("Location where your data is stored."))
        grid_layout.addWidget(data_path_label, 0, 0)

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
        locale_label.setToolTip(self.tr("Language for the application interface."))
        grid_layout.addWidget(locale_label, 1, 0)

        self.locale_combo_box = QComboBox()
        self.locale_combo_box.setPlaceholderText(self.tr("Locale"))
        self.locale_combo_box.addItems(self.translations_handler.get_available_languages())
        self.locale_combo_box.setCurrentText(self.translations_handler.get_language_name(self.settings_handler.get("system_locale")))
        self.locale_combo_box.setToolTip(self.tr("Language for the application interface."))
        self.locale_combo_box.currentTextChanged.connect(self.locale_changed)
        grid_layout.addWidget(self.locale_combo_box, 1, 1)

        # row 2: use_website_as_name
        use_website_label = QLabel(self.tr("Use website\n as name"))
        use_website_label.setToolTip(self.tr("Use the website as the entry name by default."))
        grid_layout.addWidget(use_website_label, 2, 0, alignment=Qt.AlignRight)

        self.use_website_combo_box = QComboBox()
        self.use_website_combo_box.addItems([self.tr("True"), self.tr("False")])
        self.use_website_combo_box.setCurrentText(
            self.tr("True") if self.settings_handler.get("use_website_as_name") else self.tr("False")
        )
        self.use_website_combo_box.setToolTip(self.tr("Use the website as the entry name by default."))
        grid_layout.addWidget(self.use_website_combo_box, 2, 1)

        # row 3: design
        design_label = QLabel(self.tr("Design"))
        design_label.setToolTip(self.tr("Theme for the application."))
        grid_layout.addWidget(design_label, 3, 0)

        self.design_combo = QComboBox()
        self.design_combo.setPlaceholderText(self.tr("Design"))
        self.design_combo.addItems(self.design_options)
        self.design_combo.setCurrentIndex(self.settings_handler.get("design"))
        self.design_combo.setToolTip(self.tr("Theme for the application."))
        grid_layout.addWidget(self.design_combo, 3, 1)

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

        card_layout.addLayout(grid_layout)
        card_layout.addSpacerItem(QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        card_layout.addLayout(button_layout)
        card_layout.addSpacerItem(QSpacerItem(0, 30, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.card_frame.setLayout(card_layout)

        main_layout.addWidget(self.card_frame)
        self.setLayout(main_layout)

    def set_style_sheet(self) -> None:
        self.setStyleSheet(load_stylesheets(self.styles_path, "settings_widget"))

    def browse_data_path(self) -> None:
        path = QFileDialog.getExistingDirectory(self, self.tr("Select Data Directory"), self.data_edit.text())
        if path:
            self.data_path_changed = True
            self.data_edit.setText(path)

    def locale_changed(self) -> None:
        """
        Updates the translations for the UI components of the settings widget.
        """
        self.language_changed = True
        # self.init_ui()

    def save_settings(self) -> None:
        logging.info("Saving settings")
        self.settings_handler.set("data_path", self.data_edit.text())
        self.settings_handler.set("system_locale", self.translations_handler.get_locale_name(self.locale_combo_box.currentText()))
        self.settings_handler.set("use_website_as_name", self.use_website_combo_box.currentIndex() == 0)
        self.settings_handler.set("design", self.design_combo.currentIndex())
        self.settings_handler.save()

        self.return_to_list()

    def return_to_list(self) -> None:
        if self.language_changed or self.data_path_changed:
            self.returned.emit(True)
        else:
            self.returned.emit(False)
