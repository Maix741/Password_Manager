import logging
import shutil
import os

from .create_master_pass import CreateMasterPassword
from .setup_folders import setup_folders
from .generate_password import gen_aes_key, gen_fernet_key, get_master_key_fragment
from .write_keys import write_keys
from .get_keys import get_keys

from .export_passwords import ExportPasswords
from .import_passwords import ImportPasswords


def renew_keys_and_delete_paswords(new_master: str, data_path: str) -> None:
    logging.info("Renewing all keys and removing passwords")
    try:
        shutil.rmtree(os.path.join(data_path, "passwords"))
        shutil.rmtree(os.path.join(data_path, "master"))
        shutil.rmtree(os.path.join(data_path, "keys"))

    except (FileNotFoundError, PermissionError) as e:
        logging.error(f"Error while removing previous keys/passwords: {e}")

    setup_folders(data_path)
    CreateMasterPassword(data_path, new_master).create()

    _, _, aes_fragment = gen_aes_key(new_master)
    fernet_key = gen_fernet_key()
    write_keys(data_path, aes_fragment, fernet_key)


def renew_keys_only(old_keys: tuple[str, bytes, list[str, bytes]], new_master: str, data_path: str) -> None:
    _, old_fernet, old_aes = old_keys

    CreateMasterPassword(data_path, new_master).create()
    new_aes_key, _, aes_fragment = gen_aes_key(new_master)
    new_fernet_key = gen_fernet_key()
    write_keys(data_path, aes_fragment, new_fernet_key)

    passwords: list[dict[str, str]] = ExportPasswords(
        csv_file_path="",
        passwords_path=os.path.join(data_path, "passwords"),
        keys=(old_fernet, tuple(old_aes))
        ).return_as_list()

    master_key_fragment: str = get_master_key_fragment(new_master)

    new_fernet_key, AES_key_fragment = get_keys(data_path)

    new_aes_key = master_key_fragment + str(AES_key_fragment[0]), AES_key_fragment[1]

    delete_paswords(data_path)
    setup_folders(data_path)

    if not passwords: return

    ImportPasswords(
        csv_file_path="",
        passwords_path=os.path.join(data_path, "passwords"),
        keys=(new_fernet_key, list(new_aes_key)),
        passwords_without_file=passwords
        )


def delete_paswords(data_path) -> None:
    logging.info("Renewing all keys and removing passwords")
    try:
        shutil.rmtree(os.path.join(data_path, "passwords"))

    except (FileNotFoundError, PermissionError) as e:
        logging.error(f"Error while removing previous keys/passwords: {e}")
    os.makedirs(os.path.join(data_path, "passwords"), exist_ok=True)
