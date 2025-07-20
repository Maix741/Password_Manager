# Password_Manager

A secure, cross-platform password manager with both command-line and graphical user interfaces. Store, manage, and organize your passwords securely using strong encryption.

## Features

- **Secure Storage**: Passwords are encrypted using AES and Fernet cryptography.
- **Cross-Platform**: Works on Windows, macOS, and Linux.
- **Local Storage**: All data is stored locally on your device.
- **Multi-Language Support**: Available in multiple languages.
- **Dark Mode**: Supports dark mode for better usability.
- **Master Password**: Protects access to all stored passwords.
- **Command-Line Interface**: Manage passwords directly from the terminal ([main.py](main.py)).
- **Graphical User Interface**: User-friendly GUI built with PySide6 ([main.pyw](main.pyw)).
- **Password Generation**: Generate strong, customizable passwords.
- **Import/Export**: Import and export passwords in CSV format.
- **Search & Organize**: Quickly search and manage your passwords.
- **Settings**: Customize data path, language, and appearance.

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/Maix741/Password_Manager.git
   cd Password_Manager
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

## Configure data path
### Environment Variable:
Set the `PASSWORD_MANAGER_DATA_PATH` environment variable to specify where the password database will be stored. If not set, it defaults to:

**Windows:** `C:\Users\<YourUsername>\AppData\Local\Password_manager\`

**Linux/macOS:** `/home/username/.Password_manager`

### Command-Line Argument:
You can also specify the data path when running the script by using the `--data-path` argument:
```sh
python main.pyw --data-path /path/to/your/data
```

## Usage

### Command-Line

Run the password manager in the terminal:
```sh
python main.py
```

### Graphical User Interface

Launch the GUI version:
```sh
pythonw main.pyw
```

## Directory Structure

- `main.py` – Command-line entry point
- `main.pyw` – GUI entry point
- `src/` – Core logic and modules
- `assets/` – Icons and images
- `requirements.txt` – Python dependencies

## Security

- Passwords are encrypted using both AES and Fernet algorithms.
- Master password is hashed and salted using PBKDF2-HMAC-SHA512.
- All sensitive data is stored locally.

## License

This project is licensed under the [MIT License](LICENSE).

---

**Note:** Always remember your master password. If you lose it, your stored passwords cannot be recovered.
