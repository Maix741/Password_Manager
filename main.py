from src import *


def get_input(manager: ManagerCMD) -> bool:
    manager.check_setup()
    selected_mode: str = input("Mode: ").lower().replace(" ", "")


    if selected_mode in ("add", "new"):
        manager.clear_console()
        manager.add_password()
        manager.reset_console()


    elif selected_mode in ("clear", "list", "c"):
        manager.reset_console()


    elif selected_mode in ("gen", "generate"):
        _ = manager.gen_password()


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
            remove_password(manager.data_path, name)
            print(f"\"{name}\" has been removed")

    elif selected_mode.startswith(("remove", "rm")):
        name: str = (selected_mode + ":").split(":")[1].lower().strip()
        if name in manager.password_names:
            remove_password(manager.data_path, name)
            print(f"\"{name}\" has been removed")


    elif selected_mode in ("quit", "exit", "q"):
        manager.reset_console()
        return True


    else:
        if not selected_mode:
            manager.reset_console()
        else:
            unknown_mode(manager, selected_mode)

    return False


def unknown_mode(manager: ManagerCMD, selected_mode: str) -> None:
    search_result: list[str] = search_passwords(manager.data_path, selected_mode)
    if len(search_result) == 1 and len(selected_mode) >= 5:
        manager.read_password(search_result[0])
    else:
        print("Unknown passowrd!")
        print("Did you mean: " + ", ".join(search_result))


def cmd_main() -> None:
    manager: ManagerCMD = ManagerCMD()
    running: bool = True
    while running:
        try:
            running: bool = not get_input(manager)
        except KeyboardInterrupt:
            manager.reset_console()


if __name__ == "__main__":
    cmd_main()
