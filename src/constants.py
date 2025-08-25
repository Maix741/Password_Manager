# version and app constants
__version__: str = "v1.7.5.4"
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


ALL_CONSTANTS: dict = {
    "password_min_lenght": PASSWORD_MIN_LENGHT,
    "password_max_lenght_slider": PASSWORD_MAX_LENGHT_SLIDER,
    "password_max_lenght_spinbox": PASSWORD_MAX_LENGHT_SPINBOX,
    "password_start_value": PASSWORD_START_VALUE,

    "entropy_threshold": ENTROPY_THRESHOLD,

    "inactivity_timer_lenght": INACTIVITY_TIMER_LENGHT,

    "mainwindow_default_geometry": MAINWINDOW_DEFAULT_GEOMETRY,
    "max_wrong_master_attempts": MAX_WRONG_MASTER_ATTEMPTS

}