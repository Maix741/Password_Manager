import argparse


def parse_args() -> argparse.Namespace:
    """Parse command line arguments for the password manager.

    Returns:
        argparse.Namespace: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-dp", "--data-path", type=str, required=False, help="Set data-path for application")
    parser.add_argument("-l", "--locale", type=str, required=False, help="Set locale for application")
    parser.add_argument("-uw", "--use_website_as_name", action="store_true", help="Use website as name for passwords")

    return parser.parse_args()
