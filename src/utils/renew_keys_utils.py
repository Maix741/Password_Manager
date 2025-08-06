import logging
import shutil
import os

from .create_master_pass import CreateMasterPassword
from .setup_folders import setup_folders
from .generate_password import gen_aes_key, gen_fernet_key
from .write_keys import write_keys

from .export_passwords import ExportPasswords
from .import_passwords import ImportPasswords


def renew_keys_and_delete_paswords(new_master: str, data_path: str) -> None:
    logging.info("Renewing all keys and removing passwords")
    try:
        delete_paswords(data_path)
        shutil.rmtree(os.path.join(data_path, "master"))
        shutil.rmtree(os.path.join(data_path, "keys"))

    except (FileNotFoundError, PermissionError) as e:
        logging.error(f"Error while removing previous keys/passwords: {e}")

    setup_folders(data_path)
    creator = CreateMasterPassword(data_path, new_master)
    creator.create()

    aes_key = gen_aes_key()
    fernet_key = gen_fernet_key()
    master: tuple[str, bytes] = (new_master, creator.salt)
    write_keys(data_path, aes_key, fernet_key, master)


def renew_keys_only(old_keys: tuple[str, bytes, list[str, bytes]], new_master: str, data_path: str) -> None:
    _, old_fernet, old_aes = old_keys

    creator = CreateMasterPassword(data_path, new_master)
    creator.create()
    new_aes_key = gen_aes_key()
    new_fernet_key = gen_fernet_key()

    master: tuple[str, bytes] = (new_master, creator.salt)
    write_keys(data_path, new_aes_key, new_fernet_key, master)

    passwords: list[dict[str, str]] = ExportPasswords(
        csv_file_path="",
        passwords_path=os.path.join(data_path, "passwords"),
        keys=(old_fernet, tuple(old_aes))
        ).return_as_list()

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
