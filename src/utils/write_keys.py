import logging
import os

from .encryption_handlers import AESCrypto
from .get_checksum import get_checksum
from .get_master import get_master


def write_keys(data_directory: str, AES_key_str: str, fernet_key: bytes, master: tuple[str, bytes]) -> None:
    keys_path = os.path.join(data_directory, "keys")
    if not os.path.dirname(keys_path): os.makedirs(keys_path)

    master_hash = tuple(get_master(data_directory))
    checksum: str = get_checksum(*master_hash)
    write_fernet_key(os.path.join(keys_path, "fernet.pem"), fernet_key, master, checksum)
    write_AES_key(os.path.join(keys_path, "AES.pem"), AES_key_str, master, checksum)


def write_fernet_key(key_path: str, fernet_key: bytes, master: str, checksum: str) -> None:
    try:
        with open(key_path, "w") as fernet_file:
            fernet_file.write(encrypt(fernet_key.hex(), master, checksum))

    except (FileNotFoundError, PermissionError) as e:
        logging.error(f"Error writing fernet key to {key_path}: {e}")


def write_AES_key(key_path: str, key_str: str, master: str, checksum: str) -> None:
    try:
        with open(key_path, "w") as AES_file:
            AES_file.write(encrypt("\n".join([key_str, str(os.urandom(16))]), master, checksum))

    except (FileNotFoundError, PermissionError) as e:
        logging.error(f"Error writing AES key to {key_path}: {e}")


def encrypt(key_str: str, master: tuple[str, bytes], checksum: str) -> str:
    master, salt = master
    encryption_key = (master[:16] + checksum)[:32]
    return AESCrypto().encrypt(key_str, encryption_key, salt)
