import sys

from PySide6.QtWidgets import QApplication

from src import ManagerGUI, parse_args


def main() -> None:
    """Main function to run the GUI password manager.
    This function initializes the QApplication and ManagerGUI instance, then starts the event loop.
    """
    args = parse_args()
    data_path = args.data_path or None

    app: QApplication = QApplication(sys.argv)
    player: ManagerGUI = ManagerGUI(data_path=data_path)
    player.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
