import argparse
import sys

from PySide6.QtWidgets import QApplication

from src import ManagerGUI


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-dp", "--data_path", type=str, required=False, help="Set data-path for application")
    args = parser.parse_args()

    data_path = args.data_path or None

    app: QApplication = QApplication(sys.argv)
    player: ManagerGUI = ManagerGUI(data_path=data_path)
    player.show()
    sys.exit(app.exec())
