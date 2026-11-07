#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import base64
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Încercăm să importăm suportul pentru Drag & Drop
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False

# Traduceri pentru interfață
TRANSLATIONS = {
    "ro": {
        "title": "Asistent Printare Duplex",
        "drop_box": "Trage fișierul aici\nsau\nclick pentru a selecta",
        "selected": "Fișier selectat:\n{name}",
        "portrait": "Printează\n\nPortrait",
        "landscape": "Printează\n\nLandscape",
        "default_printer": "Implicită sistem",
        "step2_title_p": "Pasul 2 - Portrait",
        "step2_msg_p": "Pune foile cu fața în jos în tavă!\n\nApasă Continuă când ești gata pentru paginile pare.",
        "step2_title_l": "Pasul 2 - Landscape",
        "step2_msg_l": "Ia foile din tava de sus și pune-le DIRECT în tava de jos (fără să le întorci)!\n\nApasă Continuă când ești gata.",
        "btn_continue": "Continuă",
        "btn_cancel": "Anulează",
        "success_title": "Succes",
        "success_msg": "Documentul a fost printat cu succes!",
        "error_title": "Eroare",
        "err_no_file": "Te rog selectează un fișier mai întâi!",
        "err_invalid": "Fișier invalid!",
        "err_libreoffice": "LibreOffice nu a fost găsit!\n\nTe rugăm să instalezi LibreOffice în versiunea .deb sau Flatpak pentru a putea converti documente care nu sunt în format PDF."
    },
    "en": {
        "title": "Duplex Print Assistant",
        "drop_box": "Drag file here\nor\nclick to select",
        "selected": "Selected file:\n{name}",
        "portrait": "Print\n\nPortrait",
        "landscape": "Print\n\nLandscape",
        "default_printer": "System Default",
        "step2_title_p": "Step 2 - Portrait",
        "step2_msg_p": "Place paper face down in the tray!\n\nPress Continue when ready for even pages.",
        "step2_title_l": "Step 2 - Landscape",
        "step2_msg_l": "Take paper from top tray and put it DIRECTLY into bottom tray (do not flip)!\n\nPress Continue when ready.",
        "btn_continue": "Continue",
        "btn_cancel": "Cancel",
        "success_title": "Success",
        "success_msg": "Document printed successfully!",
        "error_title": "Error",
        "err_no_file": "Please select a file first!",
        "err_invalid": "Invalid file!",
        "err_libreoffice": "LibreOffice was not found!\n\nPlease install LibreOffice in .deb or Flatpak version to convert non-PDF documents."
    },
    "it": {
        "title": "Assistente Stampa Fronte-Retro",
        "drop_box": "Trascina il file qui\no\nclicca per selezionare",
        "selected": "File selezionato:\n{name}",
        "portrait": "Stampa\n\nPortrait",
        "landscape": "Stampa\n\nLandscape",
        "default_printer": "Predefinita di sistema",
        "step2_title_p": "Passo 2 - Portrait",
        "step2_msg_p": "Metti i fogli a faccia in giù nel vassoio!\n\nPremi Continua quando sei pronto per le pagine pari.",
        "step2_title_l": "Passo 2 - Landscape",
        "step2_msg_l": "Prendi i fogli dal vassoio superiore e mettili DIRETTAMENTE in quello inferiore (senza girarli)!\n\nPremi Continua quando sei pronto.",
        "btn_continue": "Continua",
        "btn_cancel": "Annulla",
        "success_title": "Successo",
        "success_msg": "Documento stampato con successo!",
        "error_title": "Errore",
        "err_no_file": "Seleziona prima un file!",
        "err_invalid": "File non valido!",
        "err_libreoffice": "LibreOffice non è stato trovato!\n\nSi prega di installare LibreOffice in versione .deb o Flatpak per convertire i documenti."
    }
}


class CustomWaitDialog(tk.Toplevel):
    def __init__(self, parent, title, message, lang_dict):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x160")
        self.resizable(False, False)
        self.result = False
        self.lang = lang_dict

        self.transient(parent)
        self.grab_set()

        parent.update_idletasks()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pw = parent.winfo_width()
        ph = parent.winfo_height()

        x = px + (pw // 2) - 200
        y = py + (ph // 2) - 80
        self.geometry(f"+{x}+{y}")

        label_msg = tk.Label(
            self,
            text=message,
            font=("TkDefaultFont", 10),
            wraplength=370,
            justify="center"
        )
        label_msg.pack(expand=True, fill="both", padx=15, pady=15)

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", pady=10)

        self.btn_ok = tk.Button(
            btn_frame,
            text=self.lang["btn_continue"],
            width=14,
            command=self.on_ok
        )
        self.btn_ok.pack(side="left", padx=30, expand=True)

        self.btn_cancel = tk.Button(
            btn_frame,
            text=self.lang["btn_cancel"],
            width=12,
            command=self.on_cancel
        )
        self.btn_cancel.pack(side="right", padx=30, expand=True)

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        parent.wait_window(self)

    def on_ok(self):
        self.result = True
        self.destroy()

    def on_cancel(self):
        self.result = False
        self.destroy()


class DuplexPrinterApp:
    def __init__(self, root):
        self.root = root
        self.current_lang = "ro"
        self.t = TRANSLATIONS[self.current_lang]

        self.root.title(self.t["title"])
        self.root.geometry("340x235")
        self.root.resizable(False, False)

        # Setează iconița de imprimantă în titlebar
        self.set_window_icon()

        self.file_path = tk.StringVar()
        self.file_path.set("")
        self.selected_file_name = ""

        # --- Top Bar ---
        top_bar = tk.Frame(root)
        top_bar.pack(fill="x", padx=8, pady=(8, 2))

        self.lang_var = tk.StringVar(value="ro")
        lang_menu = ttk.Combobox(
            top_bar,
            textvariable=self.lang_var,
            values=["ro", "en", "it"],
            state="readonly",
            width=4
        )
        lang_menu.pack(side="left")
        lang_menu.bind("<<ComboboxSelected>>", self.change_language)

        self.printer_var = tk.StringVar()
        printer_list = self.get_available_printers()
        self.printer_combo = ttk.Combobox(
            top_bar,
            textvariable=self.printer_var,
            values=printer_list,
            state="readonly",
            width=20
        )
        if printer_list:
            self.printer_combo.current(0)
        self.printer_combo.pack(side="right")

        # --- Drag & Drop ---
        self.lbl_drop_info = tk.Label(
            root,
            text=self.t["drop_box"],
            font=("TkDefaultFont", 9),
            fg="#555555",
            cursor="hand2",
            justify="center",
            padx=2,
            pady=4
        )
        self.lbl_drop_info.pack(fill="x", padx=8, pady=2)
        self.lbl_drop_info.bind("<Button-1>", lambda e: self.browse_file())

        if HAS_DND:
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind("<<Drop>>", self.drop_handler)
            self.lbl_drop_info.drop_target_register(DND_FILES)
            self.lbl_drop_info.dnd_bind("<<Drop>>", self.drop_handler)

        # --- Butoane ---
        frame_buttons = tk.Frame(root)
        frame_buttons.pack(pady=4)

        self.btn_portrait = tk.Button(
            frame_buttons,
            text=self.t["portrait"],
            font=("TkDefaultFont", 10, "bold"),
            width=10,
            height=5,
            command=lambda: self.start_print("portrait")
        )
        self.btn_portrait.pack(side="left", padx=8)

        self.btn_landscape = tk.Button(
            frame_buttons,
            text=self.t["landscape"],
            font=("TkDefaultFont", 10, "bold"),
            width=15,
            height=3,
            command=lambda: self.start_print("landscape")
        )
        self.btn_landscape.pack(side="left", padx=8)

    def set_window_icon(self):
        """Setează o iconiță generică de imprimantă în bara de titlu folosind date PNG în Base64."""
        icon_base64 = (
            "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlz"
            "AAAOxAAADsQBlJ12AAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH5AMXDBEbN8Qc9AAAAB1p"
            "VFh0Q29tbWVudAAAAAAAQ3JlYXRlZCB3aXRoIEdJTVBkLmhoAAAAf0lEQVQ4y2NgGAWjADXwdG34"
            "f2x8/H8I31mIgeH/m9v/Gf6/+v4fI4xN89e1f/C5q60I42NToI4fzwygIbgx0fL0dQYGBgY4e/1U"
            "A0x1YxaghhsgA15e+M/AwMDEwAAG4A32T3f+YmBgYGBgYmJiAAn+/f8Xip9vI0kBAAnLNoQ4YfCq"
            "AAAAAElFTkSuQmCC"
        )
        try:
            self._icon_image = tk.PhotoImage(data=icon_base64)
            self.root.iconphoto(True, self._icon_image)
        except Exception:
            pass

    def get_available_printers(self):
        printers = ["Implicită sistem"]
        try:
            output = subprocess.check_output(["lpstat", "-p"], text=True)
            for line in output.splitlines():
                if line.startswith("printer"):
                    p_name = line.split()[1]
                    printers.append(p_name)
        except Exception:
            pass
        return printers

    def change_language(self, event):
        self.current_lang = self.lang_var.get()
        self.t = TRANSLATIONS[self.current_lang]
        self.root.title(self.t["title"])

        if not self.file_path.get():
            self.lbl_drop_info.config(text=self.t["drop_box"])
        else:
            self.lbl_drop_info.config(text=self.t["selected"].format(name=self.selected_file_name))

        self.btn_portrait.config(text=self.t["portrait"])
        self.btn_landscape.config(text=self.t["landscape"])

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Selectează fișierul",
            filetypes=[
                ("Toate fișierele suportate", "*.pdf *.odt *.doc *.docx *.txt"),
                ("PDF", "*.pdf"),
                ("Documente", "*.odt *.doc *.docx"),
                ("Text", "*.txt"),
            ],
        )
        if filename:
            self.file_path.set(filename)
            self.selected_file_name = os.path.basename(filename)
            self.lbl_drop_info.config(text=self.t["selected"].format(name=self.selected_file_name), fg="black")

    def drop_handler(self, event):
        path = event.data.strip("{}")
        if os.path.isfile(path):
            self.file_path.set(path)
            self.selected_file_name = os.path.basename(path)
            self.lbl_drop_info.config(text=self.t["selected"].format(name=self.selected_file_name), fg="black")
        else:
            messagebox.showerror(self.t["error_title"], self.t["err_invalid"])

    def start_print(self, mode):
        fpath = self.file_path.get().strip()
        if not fpath or not os.path.isfile(fpath):
            messagebox.showerror(self.t["error_title"], self.t["err_no_file"])
            return

        self.btn_portrait.config(state="disabled")
        self.btn_landscape.config(state="disabled")

        selected_printer = self.printer_var.get()
        printer_arg = []
        if selected_printer and selected_printer not in ["Implicită sistem", "System Default", "Predefinita di sistema"]:
            printer_arg = ["-d", selected_printer]

        try:
            temp_pdf = False
            pdf_file = fpath

            if not fpath.lower().endswith(".pdf"):
                converted = False

                # 1. Încercăm versiunea nativă (deb)
                try:
                    subprocess.run(
                        ["libreoffice", "--headless", "--convert-to", "pdf", fpath],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=True,
                    )
                    converted = True
                except (FileNotFoundError, subprocess.CalledProcessError):
                    pass

                # 2. Încercăm versiunea Flatpak
                if not converted:
                    try:
                        subprocess.run(
                            ["flatpak", "run", "org.libreoffice.LibreOffice", "--headless", "--convert-to", "pdf", fpath],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            check=True,
                        )
                        converted = True
                    except (FileNotFoundError, subprocess.CalledProcessError):
                        pass

                if not converted:
                    raise FileNotFoundError(self.t["err_libreoffice"])

                base_name = os.path.splitext(os.path.basename(fpath))[0]
                pdf_file = f"{base_name}.pdf"
                temp_pdf = True

            # Pasul 1: Printează paginile impare
            if mode == "portrait":
                cmd1 = ["lp"] + printer_arg + ["-o", "page-set=odd", pdf_file]
                subprocess.run(cmd1, check=True)

                dialog = CustomWaitDialog(self.root, self.t["step2_title_p"], self.t["step2_msg_p"], self.t)
                if not dialog.result:
                    self.cleanup_temp(temp_pdf, pdf_file)
                    return

                # Pasul 2: Printează paginile pare
                cmd2 = ["lp"] + printer_arg + ["-o", "page-set=even", "-o", "outputorder=reverse", "-o", "orientation-requested=6", pdf_file]
                subprocess.run(cmd2, check=True)

            elif mode == "landscape":
                cmd1 = ["lp"] + printer_arg + ["-o", "page-set=odd", "-o", "fit-to-page", "-o", "landscape", pdf_file]
                subprocess.run(cmd1, check=True)

                dialog = CustomWaitDialog(self.root, self.t["step2_title_l"], self.t["step2_msg_l"], self.t)
                if not dialog.result:
                    self.cleanup_temp(temp_pdf, pdf_file)
                    return

                cmd2 = ["lp"] + printer_arg + ["-o", "page-set=even", "-o", "outputorder=reverse", "-o", "fit-to-page", "-o", "landscape", pdf_file]
                subprocess.run(cmd2, check=True)

            self.cleanup_temp(temp_pdf, pdf_file)
            messagebox.showinfo(self.t["success_title"], self.t["success_msg"])

        except Exception as e:
            messagebox.showerror(self.t["error_title"], f"{str(e)}")
        finally:
            self.btn_portrait.config(state="normal")
            self.btn_landscape.config(state="normal")

    def cleanup_temp(self, temp_pdf, pdf_file):
        if temp_pdf and os.path.exists(pdf_file):
            try:
                os.remove(pdf_file)
            except Exception:
                pass


if __name__ == "__main__":
    if HAS_DND:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    app = DuplexPrinterApp(root)
    root.mainloop()
