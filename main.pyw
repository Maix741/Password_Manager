import argparse
import sys

from PySide6.QtWidgets import QApplication

from src import ManagerGUI


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-dp", "--data-path", type=str, required=False, help="Set data-path for application")

    return parser.parse_args()


if __name__ == "__main__":
    args: argparse.Namespace = parse_args()
    data_path = args.data_path or None

    app: QApplication = QApplication(sys.argv)
    player: ManagerGUI = ManagerGUI(data_path=data_path)
    player.show()
    sys.exit(app.exec())
