import argparse
import platform
import sys

from PySide6.QtWidgets import QApplication

from src import ManagerGUI


def parse_args() -> argparse.Namespace:
    """Parse command line arguments for the password manager.

    Returns:
        argparse.Namespace: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-dp", "--data-path", type=str, required=False, help="Set data-path for application")

    return parser.parse_args()


def main() -> None:
    """Main function to run the GUI password manager.
    This function initializes the QApplication and ManagerGUI instance, then starts the event loop.
    """
    args: argparse.Namespace = parse_args()
    data_path = args.data_path or None

    app: QApplication = QApplication(sys.argv)
    player: ManagerGUI = ManagerGUI(data_path=data_path)
    player.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
