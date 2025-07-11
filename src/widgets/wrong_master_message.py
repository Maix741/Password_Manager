from PySide6.QtWidgets import QMessageBox


class MasterWarningMessage(QMessageBox):
    def __init__(self, /, parent = None) -> None:
            super().__init__(parent)
            self.__init_ui()

    def __init_ui(self) -> None:
        self.setIcon(QMessageBox.Warning)
        self.setWindowTitle(self.tr("Invalid Master entered"))
        self.setText(self.tr("Invalid master password entered. Please try again "))
        ok_button = self.addButton(self.tr("OK"), QMessageBox.AcceptRole)

        if self.clickedButton() == ok_button:
            self.close()
