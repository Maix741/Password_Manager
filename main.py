import argparse

from src import ManagerCMD


def get_input(manager: ManagerCMD) -> bool:
    """Get input from the user and perform actions based on the input.

    Args:
        manager (ManagerCMD): Instance of the ManagerCMD class to manage passwords.

    Returns:
        bool: Returns True if the user wants to exit, otherwise False.
    """
    manager.check_setup()
    selected_mode: str = input("Mode: ").lower().replace(" ", "")


    if selected_mode in ("add", "new"):
        manager.clear_console()
        manager.add_password()
        manager.reset_console()


    elif selected_mode in ("clear", "list", "c"):
        manager.reset_console()


    elif selected_mode in ("gen", "generate"):
        manager.gen_password()


    elif selected_mode == "renew":
        manager.renew_keys()


    elif selected_mode in ("read", "r"):
        name: str = manager.get_password_name()
        if name in manager.password_names:
            manager.read_password(name)

    elif selected_mode in manager.password_names:
        manager.read_password(selected_mode)

    elif selected_mode.startswith("read"):
        name: str = (selected_mode + ":").split(":")[1].lower().strip()
        if name in manager.password_names:
            manager.read_password(name)


    elif selected_mode in ("remove", "rm"):
        name: str = manager.get_password_name()
        if name in manager.password_names:
            manager.remove_password(name)

    elif selected_mode.startswith(("remove", "rm")):
        name: str = (selected_mode + ":").split(":")[1].lower().strip()
        if name in manager.password_names:
            manager.remove_password(name)

    elif selected_mode in ("import", "im"):
        manager.import_passwords()

    elif selected_mode in ("export", "ex"):
        manager.export_passwords()


    elif selected_mode in ("quit", "exit", "q"):
        manager.reset_console()
        return True


    else:
        if not selected_mode:
            manager.reset_console()
        else:
            manager.search_passwords(selected_mode)

    return False


def parse_args() -> argparse.Namespace:
    """Parse command line arguments for the password manager.

    Returns:
        argparse.Namespace: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-dp", "--data-path", type=str, required=False, help="Set data-path for application")

    return parser.parse_args()


def cmd_main() -> None:
    """Main function to run the command line password manager.

    This function initializes the ManagerCMD instance and enters a loop to get user input
    until the user decides to exit.
    """
    args: argparse.Namespace = parse_args()
    data_path = args.data_path or None

    manager: ManagerCMD = ManagerCMD(data_path=data_path)
    running: bool = True
    while running:
        try:
            running: bool = not get_input(manager)
        except KeyboardInterrupt:
            manager.reset_console()


if __name__ == "__main__":
    cmd_main()
