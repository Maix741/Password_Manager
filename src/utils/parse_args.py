import argparse


def parse_args() -> argparse.Namespace:
    """Parse command line arguments for the password manager.

    Returns:
        argparse.Namespace: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-dp", "--data-path", type=str, required=False, help="Set data-path for application")

    return parser.parse_args()
