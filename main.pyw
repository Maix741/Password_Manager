import sys

from PySide6.QtWidgets import QApplication

from src import ManagerGUI


if __name__ == "__main__":
    app: QApplication = QApplication(sys.argv)
    player: ManagerGUI = ManagerGUI()
    player.show()
    sys.exit(app.exec())
