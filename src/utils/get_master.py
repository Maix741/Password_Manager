import logging
import os


def get_master(data_path: str) -> list[bytes, bytes, int]:
    master_file: str = os.path.join(data_path, "master", "master_pass.pem")
    try:
        with open(master_file, "r") as file:
            master: str = file.read() # hash, salt, iterations
            master = [bytes.fromhex(k) for k in master.split("\n")]
            master[2] = int(master[2])

    except (FileNotFoundError, PermissionError, ValueError) as e:
        logging.error(f"Error getting master from file: {e}")
        return None

    return master
