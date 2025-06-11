#!/bin/sh
pyinstaller --onefile --log-level=WARN --name main_CMD main.py
pyinstaller --onefile --add-data styles:styles --log-level=WARN --name main main.pyw
