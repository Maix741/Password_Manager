import logging
import os


def setup_logging(log_file: str) -> None:
    """Configure the logging settings for the application."""

    if not os.path.exists(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file))

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", handlers=[
        logging.FileHandler(log_file),
        # logging.StreamHandler()
    ])
