import ast
import os

from .encryption_handlers import AESCrypto
from .get_checksum import get_checksum
from  .get_master import get_master


# -> (fernet_key: bytes, (AES_key: str, salt: bytes))
def get_keys(data_directory: str, master_key: str) -> tuple[bytes, tuple[str, bytes]]:
    master_hashed, salt, iterations = get_master(data_path=data_directory)

    keys_path = os.path.join(data_directory, "keys")
    decryption_key: str = (master_key[:16] + get_checksum(master_hashed, salt, iterations))[:32]
    crypto_handler: AESCrypto = AESCrypto()

    fernet_key: bytes = get_fernet_key(os.path.join(keys_path, "fernet.pem"))
    AES_key: bytes = get_AES_key(os.path.join(keys_path, "AES.pem"))
    if not (fernet_key and AES_key): return (None, None)

    fernet_key = bytes.fromhex(crypto_handler.decrypt(fernet_key, decryption_key, salt))
    AES_key = transform_aes(crypto_handler.decrypt(AES_key, decryption_key, salt))

    return (fernet_key, AES_key)


def transform_aes(aes_string: str) -> tuple[str, bytes]:
    AES_key: list[str, bytes] = aes_string.split("\n")
    AES_key[1] = ast.literal_eval(AES_key[1])

    return tuple(AES_key)


def get_fernet_key(key_path: str) -> bytes | None:
    try:
        with open(key_path, "r") as fernet_file:
            return fernet_file.read()

    except (FileNotFoundError, PermissionError):
        return None


def get_AES_key(key_path: str) -> bytes | None:
    try:
        with open(key_path, "r") as fernet_file:
            return fernet_file.read()

    except (FileNotFoundError, PermissionError):
        return None
