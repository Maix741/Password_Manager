from functools import partial

from PySide6.QtWidgets import QInputDialog, QLineEdit, QDialog
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt

from .load_stylesheets import load_stylesheets


def open_input_dialog(parent, title: str, label: str, password: bool = False) -> str | None:
    """Open an input dialog to get user input.
    This function creates a dialog with a text input field, allowing the user to enter a string.
    If `password` is True, the input will be masked as a password.

    Args:
        parent (_type_): The parent widget for the dialog.
        title (str): The title of the dialog.
        label (str): The label text above the input field.
        password (bool, optional): Whether the input will be a password. Defaults to False.

    Returns:
        str | None: The user input if the dialog is accepted, otherwise None.
    """

    def show_hide_text(dialog: QInputDialog, action: QAction) -> None:
        """Toggle the visibility of the text in the line-edit."""
        if dialog.textEchoMode() == QLineEdit.Password:
            dialog.setTextEchoMode(QLineEdit.Normal)
            action.setIcon(parent.hide_icon)
        else:
            dialog.setTextEchoMode(QLineEdit.Password)
            action.setIcon(parent.show_icon)

    def add_show_action(dialog: QInputDialog) -> None:
        """Add a show/hide password action to the line-edit."""
        # grab the line-edit that QInputDialog uses internally
        line_edit: QLineEdit | None = dialog.findChild(QLineEdit)
        if line_edit is None:
            return  # should never happen

        # add the action to the trailing (right) side of the line-edit
        show_action: QAction = line_edit.addAction(
            parent.show_icon, QLineEdit.TrailingPosition
        )
        show_action.setToolTip(parent.tr("Show/Hide Password"))
        show_action.setCheckable(True)
        show_action.triggered.connect(partial(show_hide_text, dialog, show_action))

    dialog: QInputDialog = QInputDialog(parent)

    dialog.setWindowTitle(title)
    dialog.setLabelText(label)
    dialog.setTextValue("")
    dialog.setTextEchoMode(QLineEdit.Password if password else QLineEdit.Normal)

    # styling / window flags
    dialog.setWindowFlags(
        Qt.WindowType.Window
        | Qt.WindowType.WindowTitleHint
        | Qt.WindowType.CustomizeWindowHint
    )
    dialog.setWindowIcon(parent.window_icon)
    dialog.setStyleSheet(load_stylesheets(parent.styles_path, "input_dialog", parent.settings_handler.get_design()))

    # if the field is a password, add the show/hide button
    if password:
        add_show_action(dialog)

    # run the dialog
    if dialog.exec_() == QDialog.Accepted:
        return dialog.textValue()
    return None
