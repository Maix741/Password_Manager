import os


def write_keys(data_directory: str, AES_key_str: str, fernet_key: bytes) -> None:
    keys_path = os.path.join(data_directory, "keys")
    if not os.path.dirname(keys_path): os.makedirs(keys_path)

    write_fernet_key(os.path.join(keys_path, "fernet.pem"), fernet_key)
    write_AES_key(os.path.join(keys_path, "AES.pem"), AES_key_str)


def write_fernet_key(key_path: str, fernet_key) -> None:
    try:
        with open(key_path, "wb") as fernet_file:
            fernet_file.write(fernet_key)

    except (FileNotFoundError, PermissionError): ...


def write_AES_key(key_path: str, key_str: str) -> None:
    try:
        with open(key_path, "w") as AES_file:
            AES_file.write("\n".join([key_str, str(os.urandom(16))]))

    except (FileNotFoundError, PermissionError): ...
