import pyperclip


class WarningMessage(QMessageBox):
    def __init__(self, /, parent = None) -> None:
            super().__init__(parent)
            self.__init_ui()

    def __init_ui(self) -> None:
        self.setIcon(QMessageBox.Warning)
        self.setWindowTitle(self.tr("Unable to copy text"))
        self.setText(self.tr("Unable to copy the text to clipboard. "))
        ok_button = self.addButton(self.tr("OK"), QMessageBox.AcceptRole)

        if self.clickedButton() == ok_button:
            self.close()


def copy_string(string: str, show_warning: bool = False) -> bool:
    """Copy a string to the clipboard.
    This function attempts to copy a given string to the clipboard using the `pyperclip` library.
    If an error occurs during the copying process, it raises a `pyperclip.PyperclipException`.
    If `show_warning` is set to True, a warning message dialog will be displayed.
    If `show_warning` is False, it will print an error message to the console.
    If the copying is successful, it returns True; otherwise, it returns False.

    Args:
        string (str): The string to be copied to the clipboard.
        show_warning (bool, optional): Show a warning message as a GUI. Defaults to False.

    Returns:
        bool: True if the string was copied successfully, False otherwise.
    """
    try:
        pyperclip.copy(string)
        return True

    except pyperclip.PyperclipException:
        if show_warning:
            global QMessageBox
            from PySide6.QtWidgets import QMessageBox
            WarningMessage().exec()
        else:
            print(f"Unable to copy the text: {string}")

        return False
