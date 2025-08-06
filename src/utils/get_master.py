import logging
import json
import os


def get_master(data_path: str) -> list[bytes, bytes, int]:
    master_file: str = os.path.join(data_path, "master", "master_pass.pem")
    try:
        with open(master_file, "r") as file:
            master: dict[bytes, bytes, int] = json.loads(file.read()) # hash, salt, iterations
            master = [bytes.fromhex(k) for k in master.values()]

    except (FileNotFoundError, PermissionError) as e:
        logging.error(f"Error getting master from file: {e}")
        return None

    return master
