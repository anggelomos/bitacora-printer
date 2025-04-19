# bitacora-printer

Script that generates daily and weekly PDF bitacora pages ready for printing. It fetches tasks from TickTick, generates stats, and includes QR codes for associated journal entries.

## Features

*   Generates daily bitacora pages including:
    *   Date and day number.
    *   Tasks categorized into Work (Great/Amazing) and Personal (Great/Amazing).
    *   Weather forecast for Quebec City (temperature, feels like, icon).
    *   Personal stats (work time, focus time, sleep time, leisure time).
    *   QR code linking to the daily journal entry.
*   Generates weekly bitacora pages including:
    *   Week number and date range.
    *   Weekly tasks categorized similarly to daily tasks.
*   Generates reflection pages.
*   Saves generated pages as PDF files.
*   Optionally opens the generated PDF after saving.

## Usage

1.  Install dependencies: `poetry install`
2.  Run the script: `poetry run python main.py`
    *   The script will prompt for date offsets and whether to print the weekly page.

## Compiling

To compile the script into a standalone executable using PyInstaller, run the following PowerShell commands from the project root:

```powershell
# Ensure dependencies are installed
poetry install --no-dev

# Run PyInstaller using the spec file
poetry run pyinstaller bitacora_printer.spec --noconfirm

# Move required assets into the executable's internal directory
# (Adjust paths if your PyInstaller output differs)
Move-Item .\dist\bitacora_printer\_internal\designs\, .\dist\bitacora_printer\_internal\fonts\ .\dist\bitacora_printer\
```

This will create an executable in the `dist/bitacora_printer` directory.
