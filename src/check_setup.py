import os


def check_setup(data_path: str) -> bool:
    os.makedirs(os.path.join(data_path, "log"), exist_ok=True)
    os.makedirs(os.path.join(data_path, "passwords"), exist_ok=True)
    os.makedirs(os.path.join(data_path, "keys"), exist_ok=True)
    os.makedirs(os.path.join(data_path, "master"), exist_ok=True)

    checks: list[bool] = []
    checks.append(os.path.exists(os.path.join(data_path, "keys", "AES.pem")))
    checks.append(os.path.exists(os.path.join(data_path, "keys", "fernet.pem")))

    checks.append(os.path.exists(os.path.join(data_path, "master", "master_pass.pem")))

    return all(checks)
