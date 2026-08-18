import os
import subprocess
import threading
import webbrowser
import tkinter as tk
from tkinter import scrolledtext

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON  = os.path.join(APP_DIR, "venv", "Scripts", "python.exe")
PORT    = 5005

BG      = "#1c1c1e"
SURFACE = "#2c2c2e"
FG      = "#f5f5f5"
FG_DIM  = "#888888"
GREEN   = "#4ADE80"
RED     = "#F87171"
BRAND   = "#d4845a"


class Panel(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Terramia")
        self.configure(bg=BG)
        self.resizable(False, False)
        self._proc = None
        self._build()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"420x320+{(sw-420)//2}+{(sh-320)//2}")
        self.protocol("WM_DELETE_WINDOW", self._cerrar)

    def _build(self):
        tk.Label(self, text="🏺  Terramia", font=("Segoe UI", 13, "bold"),
                 bg=BG, fg=FG, pady=14).pack()

        # Indicador de estado
        self._estado = tk.Label(self, text="● Detenido",
                                font=("Segoe UI", 10), bg=BG, fg=RED)
        self._estado.pack()

        # Botones
        f = tk.Frame(self, bg=BG, pady=14)
        f.pack()
        self._btn_start = self._btn(f, "▶  Iniciar", GREEN, self._iniciar)
        self._btn_start.pack(side="left", padx=6)
        self._btn_stop = self._btn(f, "⏹  Detener", RED, self._detener, False)
        self._btn_stop.pack(side="left", padx=6)
        self._btn(f, "🌐  Abrir", BRAND, lambda: webbrowser.open(f"http://localhost:{PORT}")).pack(side="left", padx=6)

        # Log
        self._log = scrolledtext.ScrolledText(
            self, height=8, font=("Consolas", 8),
            bg=SURFACE, fg=FG_DIM, relief="flat", state="disabled"
        )
        self._log.pack(fill="x", padx=12, pady=(0, 12))

    def _btn(self, parent, text, color, cmd, enabled=True):
        b = tk.Button(parent, text=text, font=("Segoe UI", 9, "bold"),
                      bg=SURFACE, fg=FG, relief="flat", cursor="hand2",
                      padx=12, pady=7, state="normal" if enabled else "disabled",
                      command=cmd)
        b.bind("<Enter>", lambda e: b.config(bg=color, fg=BG) if str(b["state"]) == "normal" else None)
        b.bind("<Leave>", lambda e: b.config(bg=SURFACE, fg=FG) if str(b["state"]) == "normal" else None)
        return b

    def _iniciar(self):
        self._proc = subprocess.Popen(
            [PYTHON, "app.py"], cwd=APP_DIR,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace", bufsize=1,
        )
        self._estado.config(text="● Corriendo", fg=GREEN)
        self._btn_start.config(state="disabled", bg=SURFACE, fg=FG)
        self._btn_stop.config(state="normal")
        threading.Thread(target=self._leer_salida, daemon=True).start()

    def _leer_salida(self):
        for line in self._proc.stdout:
            self.after(0, self._log_append, line.rstrip())
        self.after(0, self._parado)

    def _detener(self):
        if self._proc:
            self._proc.terminate()

    def _parado(self):
        self._estado.config(text="● Detenido", fg=RED)
        self._btn_start.config(state="normal")
        self._btn_stop.config(state="disabled", bg=SURFACE, fg=FG)

    def _log_append(self, text):
        self._log.config(state="normal")
        self._log.insert("end", text + "\n")
        self._log.see("end")
        self._log.config(state="disabled")

    def _cerrar(self):
        self._detener()
        self.destroy()


if __name__ == "__main__":
    Panel().mainloop()
