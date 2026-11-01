# Duplex Print Assistant

A small Linux desktop utility that lets you **print double-sided (duplex) on printers that don't support automatic duplexing**. It guides you through printing the odd pages first, then the even pages on the reverse side of the same sheets.

Built with Python and Tkinter on top of CUPS.

## Features

- **Manual duplex printing** in two steps: odd pages first, then even pages in reverse order.
- **Portrait and Landscape modes**, each with its own paper-handling instructions.
- **Drag & drop** support for files (optional, via `tkinterdnd2`), or click to browse.
- **Printer selection** from the CUPS printers detected on your system, or the system default.
- **Automatic conversion to PDF** for `.odt`, `.doc`, `.docx` and `.txt` files using LibreOffice (native `.deb` or Flatpak). Temporary PDFs are cleaned up after printing.
- **Multilingual interface**: Romanian, English and Italian, switchable at runtime.
- Step-by-step dialogs telling you how to reload the paper before the second pass.

## How it works

1. Select a file (PDF, ODT, DOC, DOCX or TXT) and a printer.
2. Choose **Portrait** or **Landscape**.
3. The app prints the odd pages with `lp -o page-set=odd`.
4. A dialog asks you to put the printed sheets back in the tray:
   - **Portrait**: face down.
   - **Landscape**: move the sheets from the output tray directly to the input tray, without flipping them.
5. After you press **Continue**, the even pages are printed in reverse order (`outputorder=reverse`) on the back of the sheets.

Landscape mode also applies `fit-to-page` and `landscape` options to both passes.

## Requirements

- Linux with **CUPS** (`lp` and `lpstat` commands available)
- Python 3 with Tkinter (`python3-tk`)
- *Optional:* [`tkinterdnd2`](https://pypi.org/project/tkinterdnd2/) for drag & drop
- *Optional:* **LibreOffice** (`.deb` or Flatpak version) to print non-PDF documents

## Installation

```bash
sudo apt install python3-tk
pip install tkinterdnd2   # optional, enables drag & drop
```

## Usage

```bash
python3 duplex.py
```

## Notes

- Paper orientation and the way sheets come out of the printer differ between models, so you may need to experiment once to find the right way to reload the paper.
- Converted PDFs are created in the current working directory and removed after printing.
