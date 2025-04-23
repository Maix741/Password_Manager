import ast
import os


# -> fernet_key: bytes, (AES_key: str, salt: bytes)
def get_keys(data_directory: str) -> tuple[bytes, tuple[str, bytes]]:
    keys_path = os.path.join(data_directory, "keys")

    fernet_key: bytes = get_fernet_key(os.path.join(keys_path, "fernet.pem"))
    AES_key: tuple[str, bytes] = get_AES_key(os.path.join(keys_path, "AES.pem"))

    return (fernet_key, AES_key)


def get_fernet_key(key_path: str) -> bytes:
    try:
        with open(key_path, "rb") as fernet_file:
            fernet_key: bytes = fernet_file.read()

    except (FileNotFoundError, PermissionError):
        fernet_key: None = None

    return fernet_key


def get_AES_key(key_path: str) -> tuple[str, bytes]:
    try:
        with open(key_path, "r") as fernet_file:
            AES_key: list[str] = fernet_file.readlines()

        AES_key[1] = ast.literal_eval(AES_key[1])
        AES_key[0] = AES_key[0].strip()

    except (FileNotFoundError, PermissionError):
        AES_key: list[str] = []

    return tuple(AES_key)
