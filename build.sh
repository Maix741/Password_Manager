# This script builds the Python application using PyInstaller for linux.
# It creates two executables: one for command line and one with a GUI.

#!/bin/sh
pyinstaller --onefile --log-level=WARN --name main_CMD main.py
pyinstaller --onefile --add-data styles:styles --log-level=WARN --name main main.pyw
