import subprocess
import platform
import os


def is_dark_mode() -> bool:
    system = platform.system()
    if system == "Windows":
        try:
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 0  # 0 = dark, 1 = light
        except Exception:
            return False

    elif not system == "Linux": #  default to light on other OS
        return False

    # Try GNOME (GTK-based)
    try:
        theme = subprocess.check_output(
            ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
            stderr=subprocess.DEVNULL
        ).decode().strip().strip("'").lower()
        if "dark" in theme:
            return True
    except Exception:
        pass

    # Try KDE Plasma
    try:
        kdeglobals = os.path.expanduser("~/.config/kdeglobals")
        if os.path.exists(kdeglobals):
            with open(kdeglobals, "r") as f:
                for line in f:
                    if line.strip().startswith("ColorScheme=") and "dark" in line.lower():
                        return True
    except Exception:
        pass

    # Try XFCE
    try:
        theme = subprocess.check_output(
            ["xfconf-query", "--channel", "xsettings", "--property", "/Net/ThemeName"],
            stderr=subprocess.DEVNULL
        ).decode().strip().lower()
        if "dark" in theme:
            return True
    except Exception:
        pass

    # Try Cinnamon
    try:
        theme = subprocess.check_output(
            ["gsettings", "get", "org.cinnamon.desktop.interface", "gtk-theme"],
            stderr=subprocess.DEVNULL
        ).decode().strip().strip("'").lower()
        if "dark" in theme:
            return True
    except Exception:
        pass

    # Try MATE
    try:
        theme = subprocess.check_output(
            ["gsettings", "get", "org.mate.interface", "gtk-theme"],
            stderr=subprocess.DEVNULL
        ).decode().strip().strip("'").lower()
        if "dark" in theme:
            return True
    except Exception:
        pass

    # Try elementary Pantheon
    try:
        theme = subprocess.check_output(
            ["gsettings", "get", "io.elementary.desktop.interface", "gtk-theme"],
            stderr=subprocess.DEVNULL
        ).decode().strip().strip("'").lower()
        if "dark" in theme:
            return True
    except Exception:
        pass

    return False  # Default to light on other OS or if detection fails
