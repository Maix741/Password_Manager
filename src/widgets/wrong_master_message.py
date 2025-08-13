from PySide6.QtWidgets import QMessageBox

from .load_stylesheets import load_stylesheets


class MasterWarningMessage(QMessageBox):
    def __init__(self, styles_path: str = "", parent = None) -> None:
        super().__init__(parent)
        self.settings_handler = parent.settings_handler

        self.styles_path: str = styles_path
        self.init_ui()

    def init_ui(self) -> None:
        self.setIcon(QMessageBox.Warning)
        self.setWindowTitle(self.tr("Invalid Master entered"))
        self.setText(self.tr("Invalid master password entered. \nPlease try again "))
        ok_button = self.addButton(self.tr("OK"), QMessageBox.AcceptRole)

        if self.clickedButton() == ok_button:
            self.close()

    def set_style_sheet(self) -> None:
        self.setStyleSheet(load_stylesheets(self.styles_path, "master_warning_message", self.settings_handler.get_design()))
