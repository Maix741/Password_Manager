# version and app constants
__version__: str = "v1.6.4"
__app_name__: str = "Password Manager"

__license__: str = "MIT"
__copyright__: str = "Copyright (c) 2025 Maix741"

__url__: str = "https://www.github.com/Maix741/Password_Manager"
__author__: str = "Maix741"
__maintainer__: str = "Maix741"

__all_version_info__: dict[str, str] = {
    "__version__": __version__,
    "__app_name__": __app_name__,
    "__license__": __license__,
    "__copyright__": __copyright__,
    "__url__": __url__,
    "__author__": __author__,
    "__maintainer__": __maintainer__,
}


# password constants
PASSWORD_MIN_LENGHT: int = 4
PASSWORD_MAX_LENGHT_SLIDER: int = 64
PASSWORD_MAX_LENGHT_SPINBOX: int = 200
PASSWORD_START_VALUE: int = 12

# password strenght constants
ENTROPY_THRESHOLD: int = 60

# read_password_constants
INACTIVITY_TIMER_LENGHT: int = 120000

# mainwindow constants
MAINWINDOW_DEFAULT_GEOMETRY: tuple[int] = (100, 100, 1000, 600)
MAX_WRONG_MASTER_ATTEMPTS: int = 10


MAINWINDOW_CONSTANTS: tuple = (
    MAINWINDOW_DEFAULT_GEOMETRY,
    MAX_WRONG_MASTER_ATTEMPTS
)

UI_CONSTANTS: tuple = (
    MAINWINDOW_DEFAULT_GEOMETRY
)
PASSWORD_CONSTANTS: tuple = (
    PASSWORD_MIN_LENGHT,
    PASSWORD_MAX_LENGHT_SPINBOX,
    PASSWORD_MAX_LENGHT_SLIDER,
    PASSWORD_START_VALUE
)
