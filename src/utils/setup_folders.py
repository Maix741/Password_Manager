import os


def setup_folders(data_directory: str) -> None:
    os.makedirs(data_directory, exist_ok=True)
    os.makedirs(os.path.join(data_directory, "master"), exist_ok=True)
    os.makedirs(os.path.join(data_directory, "passwords"), exist_ok=True)
    os.makedirs(os.path.join(data_directory, "log"), exist_ok=True)
    os.makedirs(os.path.join(data_directory, "keys"), exist_ok=True)
    os.makedirs(os.path.join(data_directory, "locales"), exist_ok=True)
