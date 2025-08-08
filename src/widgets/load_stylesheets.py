import logging
import os
import re


def extract_css_variables(theme_path: str) -> dict:
    """
    Extracts CSS variables from a :root block in a CSS file.
    Returns a dict mapping variable names to their values.
    """
    variables = {}
    with open(theme_path, "r", encoding="utf-8") as f:
        content = f.read()
    root_match = re.search(r":root\s*{([^}]*)}", content, re.DOTALL)
    if root_match:
        for line in root_match.group(1).splitlines():
            line = line.strip().rstrip(";")
            if line.startswith("--"):
                name, value = line.split(":", 1)
                variables[name.strip()] = value.strip()
    return variables


def preprocess_qss(qss: str, variables: dict) -> str:
    """
    Replaces var(--variable) with the value from variables dict.
    """
    def replacer(match):
        var_name = match.group(1)
        return variables.get(var_name, match.group(0))
    # Remove the :root block entirely
    qss = re.sub(r":root\s*{[^}]*}", "", qss, flags=re.DOTALL)
    # Replace var(--variable) with actual value
    return re.sub(r"var\((--[\w-]+)\)", replacer, qss)


def load_stylesheets(styles_path: str, widget_name: str, design: int = 0) -> str:
    """
    Loads and preprocesses theme.css and widget css, replacing CSS variables for Qt compatibility.
    """
    if design == 1:
        theme_file = os.path.join(styles_path, "theme_dark.css")
    else:
        theme_file = os.path.join(styles_path, "theme_light.css")

    widget_file = os.path.join(styles_path, f"{widget_name}.css")
    qss: str = ""
    try:
        variables = extract_css_variables(theme_file)
    except (FileNotFoundError, PermissionError) as e:
        logging.exception(
            f"Error getting {theme_file} for the {widget_name}: {e}"
        )
        return qss

    for file in [theme_file, widget_file]:
        try:
            with open(file, "r", encoding="utf-8") as f:
                raw = f.read()
                qss += preprocess_qss(raw, variables) + "\n"

        except (FileNotFoundError, PermissionError) as e:
            logging.exception(
                f"Error getting {os.path.basename(file)} for the {widget_name}: {e}"
            )

    return qss
