import string  # For checking character diversity
import math  # For entropy calculation

from .constants import PASSWORD_MIN_LENGHT, ENTROPY_THRESHOLD


def calculate_entropy(password: str) -> float:
    """Calculates entropy based on character diversity and length."""
    charset_size = 0
    if any(c in string.ascii_lowercase for c in password):
        charset_size += 26
    if any(c in string.ascii_uppercase for c in password):
        charset_size += 26
    if any(c in string.digits for c in password):
        charset_size += 10
    if any(c in string.punctuation for c in password):
        charset_size += len(string.punctuation)
    if any(c.isspace() for c in password):
        charset_size += 1
    
    return len(password) * math.log2(charset_size) if charset_size else 0.0


def check_password_strength(password: str) -> bool:
    """Evaluates password strength based on entropy and diversity."""
    entropy: int = calculate_entropy(password)

    # Classifying password strength
    if entropy > ENTROPY_THRESHOLD and not len(password) < PASSWORD_MIN_LENGHT:
        return True
    else:
        return False


def check_password_duplication(all_passwords: list[dict]) -> list[list[dict]]:
    """Checks for duplicate passwords in the provided list.
    Returns a list of lists, where each inner list contains entries with the same reused password.
    """
    from collections import defaultdict

    password_map = defaultdict(list)
    for entry in all_passwords:
        password = entry.get("password")
        if password:
            password_map[password].append(entry)

    # Only include lists with more than one entry
    duplicates = [entries for entries in password_map.values() if len(entries) > 1]
    return duplicates
