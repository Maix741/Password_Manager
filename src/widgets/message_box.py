from PySide6.QtWidgets import QMessageBox

from .load_stylesheets import load_stylesheets


class MessageBox(QMessageBox):
    def __init__(self, styles_path: str, settings_handler, parent=None) -> None:
        super().__init__(parent)
        self.styles_path = styles_path
        self.settings_handler = settings_handler
        self.setStyleSheet(load_stylesheets(self.styles_path, "message_box", self.settings_handler.get_design()))

    def warn(self, title: str, text: str) -> bool:
        """Display a warning message box with the given title and text.

        Args:
            title (str): title of the message box.
            text (str): text to display in the message box.

        Returns:
            bool: True if the user clicked 'OK', False if 'Cancel' was clicked.
        """
        self.setIcon(QMessageBox.Warning)
        self.setWindowTitle(title)
        self.setText(text)
        ok_button = self.addButton(self.tr("Ok"), QMessageBox.AcceptRole)
        self.addButton(self.tr("Cancel"), QMessageBox.RejectRole)
        self.exec()

        return self.clickedButton() == ok_button

    def info(self, title: str, text: str) -> None:
        """Display an informational message box.

        Args:
            title (str): title of the message box.
            text (str): text to display in the message box.
        """
        self.setIcon(QMessageBox.Information)
        self.setWindowTitle(title)
        self.setText(text)
        self.exec()
    
    def critical(self, title: str, text: str) -> None:
        """Display a critical error message box.

        Args:
            title (str): title of the message box.
            text (str): text to display in the message box.
        """
        self.setIcon(QMessageBox.Critical)
        self.setWindowTitle(title)
        self.setText(text)
        self.exec()
    
    def question(self, title: str, text: str) -> bool:
        """Display a question message box with 'Yes' and 'No' options.

        Args:
            title (str): title of the message box.
            text (str): text to display in the message box.

        Returns:
            bool: True if the user clicked 'Yes', False if 'No' was clicked.
        """
        self.setIcon(QMessageBox.Question)
        self.setWindowTitle(title)
        self.setText(text)
        yes_button = self.addButton(self.tr("Yes"), QMessageBox.YesRole)
        no_button = self.addButton(self.tr("No"), QMessageBox.NoRole)
        self.exec()
        
        return self.clickedButton() == yes_button
