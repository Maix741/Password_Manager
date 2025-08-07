import hashlib
import logging
import sys


def get_checksum(master_hashed: bytes, salt: bytes, iterations: int) -> str:
    """Generate a checksum using PBKDF2-HMAC-SHA256.

    Args:
        master_hashed (bytes): The hashed master password.
        salt (bytes): The salt used for hashing.
        iterations (int): The number of iterations for the hashing algorithm.

    Returns:
        str: The resulting checksum as a hexadecimal string.
    """
    try:
        checksum = hashlib.pbkdf2_hmac(
            "sha256",
            master_hashed,
            salt,
            iterations
        )
        return checksum.hex()
    except Exception as e:
        logging.error(f"Error generating checksum: {e}")
        sys.exit(1)
