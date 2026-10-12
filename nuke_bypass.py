import os
import sys
import shutil
import tempfile
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

APP_NAME = "NUKE BYPASS TWEAKER"
BG = "#11110f"
PANEL = "#1b1a17"
PANEL_2 = "#24221e"
ORANGE = "#e86c36"
ORANGE_HI = "#ff7c45"
TEXT = "#f3eee7"
MUTED = "#aaa39a"
GREEN = "#83c98a"

class NukeTweaker:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("1000x700")
        self.root.minsize(850, 600)
        self.root.configure(bg=BG)
        self.busy = False
        self.banner_photo = None
        self._setup_style()
        self._build_ui()

    def _setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TProgressbar", troughcolor=PANEL_2, background=ORANGE,
                        bordercolor=PANEL_2, lightcolor=ORANGE, darkcolor=ORANGE)

    def _build_ui(self):
        # Header artwork based on the supplied NUKE BYPASS banner.
        header = tk.Frame(self.root, bg=BG, height=230)
        header.pack(fill="x", padx=18, pady=(18, 10))
        header.pack_propagate(False)
        banner_path = Path(__file__).with_name("banner.jpg")
        if PIL_AVAILABLE and banner_path.exists():
            try:
                im = Image.open(banner_path)
                im.thumbnail((1500, 320), Image.Resampling.LANCZOS)
                self.banner_photo = ImageTk.PhotoImage(im)
                tk.Label(header, image=self.banner_photo, bg=BG, bd=0).pack(fill="both", expand=True)
            except Exception:
                self._fallback_header(header)
        else:
            self._fallback_header(header)

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=24, pady=(0, 18))

        left = tk.Frame(body, bg=PANEL, highlightbackground="#39342d", highlightthickness=1)
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))
        tk.Label(left, text="SYSTEM STATUS", bg=PANEL, fg=ORANGE, font=("Segoe UI", 11, "bold")).pack(
            anchor="w", padx=20, pady=(18, 8))
        self.status_var = tk.StringVar(value="READY — waiting for your command")
        tk.Label(left, textvariable=self.status_var, bg=PANEL, fg=TEXT, font=("Segoe UI", 11),
                 wraplength=520, justify="left").pack(anchor="w", padx=20, pady=(0, 16))

        self.progress = ttk.Progressbar(left, mode="determinate", maximum=100, value=0)
        self.progress.pack(fill="x", padx=20, pady=(0, 16))

        tk.Label(left, text="TWEAK OPTIONS", bg=PANEL, fg=ORANGE, font=("Segoe UI", 11, "bold")).pack(
            anchor="w", padx=20, pady=(0, 10))
        self.clean_var = tk.BooleanVar(value=True)
        self.report_var = tk.BooleanVar(value=True)
        self.power_var = tk.BooleanVar(value=False)
        self._check(left, "Clean temporary files (current user)", self.clean_var)
        self._check(left, "Show system summary after scan", self.report_var)
        self._check(left, "Switch to High Performance power plan (optional)", self.power_var)

        self.log = tk.Text(left, height=7, bg="#0e0e0d", fg="#d9d2c8", insertbackground=TEXT,
                           relief="flat", font=("Consolas", 9), wrap="word", state="disabled")
        self.log.pack(fill="both", expand=True, padx=20, pady=(14, 18))
        self._log("NUKE BYPASS initialized.")
        self._log("Choose your options, then press TWEAK.")
        self._log("No Windows services or security features are disabled by default.")

        right = tk.Frame(body, bg=BG, width=230)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        tk.Label(right, text="READY TO DEPLOY?", bg=BG, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(pady=(12, 8))
        tk.Label(right, text="Run selected maintenance\nwith a single click.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 10), justify="center").pack(pady=(0, 18))

        self.tweak_btn = tk.Button(right, text="TWEAK", command=self.run_tweaks,
                                   bg=ORANGE, fg="#11100e", activebackground=ORANGE_HI,
                                   activeforeground="#11100e", bd=0, relief="flat",
                                   font=("Segoe UI Black", 22, "bold"), cursor="hand2",
                                   height=2)
        self.tweak_btn.pack(fill="x", padx=4, pady=(0, 12), ipady=8)

        tk.Button(right, text="SYSTEM INFO", command=self.show_system_info,
                  bg=PANEL_2, fg=TEXT, activebackground="#33302a", activeforeground=TEXT,
                  bd=0, font=("Segoe UI", 10, "bold"), cursor="hand2").pack(fill="x", padx=4, pady=5, ipady=10)
        tk.Button(right, text="OPEN TEMP FOLDER", command=self.open_temp,
                  bg=PANEL_2, fg=TEXT, activebackground="#33302a", activeforeground=TEXT,
                  bd=0, font=("Segoe UI", 10, "bold"), cursor="hand2").pack(fill="x", padx=4, pady=5, ipady=10)
        tk.Button(right, text="EXIT", command=self.root.destroy,
                  bg="#30201a", fg=ORANGE_HI, activebackground="#493025",
                  activeforeground=ORANGE_HI, bd=0, font=("Segoe UI", 10, "bold"),
                  cursor="hand2").pack(fill="x", padx=4, pady=(18, 5), ipady=9)

        tk.Label(self.root, text="NUKE BYPASS  •  LOCAL PC UTILITY  •  REVIEW CHANGES BEFORE APPLYING",
                 bg=BG, fg="#706a61", font=("Segoe UI", 8)).pack(pady=(0, 10))

    def _fallback_header(self, parent):
        tk.Label(parent, text="NUKE BYPASS", bg="#171613", fg=ORANGE,
                 font=("Impact", 42, "bold")).pack(fill="both", expand=True)
        tk.Label(parent, text="TWEAK YOUR PC • KEEP CONTROL", bg="#171613", fg=TEXT,
                 font=("Segoe UI", 11, "bold")).pack()

    def _check(self, parent, label, variable):
        tk.Checkbutton(parent, text=label, variable=variable, bg=PANEL, fg=TEXT,
                       activebackground=PANEL, activeforeground=TEXT, selectcolor=PANEL_2,
                       font=("Segoe UI", 10), anchor="w", padx=0).pack(fill="x", padx=20, pady=3)

    def _log(self, message):
        self.log.configure(state="normal")
        self.log.insert("end", f"> {message}\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _set_status(self, message):
        self.status_var.set(message)

    def run_tweaks(self):
        if self.busy:
            return
        if not any((self.clean_var.get(), self.report_var.get(), self.power_var.get())):
            messagebox.showinfo(APP_NAME, "Select at least one option first.")
            return
        warning = "This will run only the options you selected. Close apps that may be using temporary files.\n\nContinue?"
        if not messagebox.askyesno(APP_NAME, warning):
            return
        self.busy = True
        self.tweak_btn.configure(state="disabled", text="WORKING...")
        self.progress.configure(value=0)
        threading.Thread(target=self._work, daemon=True).start()

    def _work(self):
        tasks = []
        if self.clean_var.get():
            tasks.append(("Cleaning temporary files", self._clean_temp))
        if self.power_var.get():
            tasks.append(("Applying optional power plan", self._high_performance))
        if self.report_var.get():
            tasks.append(("Collecting system summary", self._system_summary))
        total = max(len(tasks), 1)
        for i, (label, func) in enumerate(tasks, start=1):
            self.root.after(0, self._set_status, label + "...")
            self.root.after(0, self._log, label + "...")
            try:
                result = func()
                self.root.after(0, self._log, result)
            except Exception as e:
                self.root.after(0, self._log, f"Skipped / error: {e}")
            self.root.after(0, self.progress.configure, {"value": int(i * 100 / total)})
        self.root.after(0, self._finish)

    def _clean_temp(self):
        temp = Path(tempfile.gettempdir())
        removed = 0
        skipped = 0
        # Only remove children of the current user's temp folder, never the folder itself.
        for item in temp.iterdir():
            try:
                if item.is_dir() and not item.is_symlink():
                    shutil.rmtree(item)
                else:
                    item.unlink()
                removed += 1
            except (PermissionError, OSError):
                skipped += 1
        return f"Temp cleanup finished: {removed} item(s) removed; {skipped} skipped/in use."

    def _high_performance(self):
        if os.name != "nt":
            return "Power plan is available only on Windows."
        import subprocess
        # Uses the built-in Windows powercfg command; it may require elevated permissions.
        p = subprocess.run(["powercfg", "/setactive", "SCHEME_MIN"],
                           capture_output=True, text=True, timeout=15)
        if p.returncode == 0:
            return "High Performance power plan selected. Power use/heat may increase."
        return "Could not change power plan. Try running as administrator or keep this option off."

    def _system_summary(self):
        import platform
        return f"System: {platform.system()} {platform.release()} | Version: {platform.version()} | Architecture: {platform.machine()}"

    def show_system_info(self):
        import platform
        info = (f"Operating system: {platform.system()} {platform.release()}\n"
                f"Architecture: {platform.machine()}\n"
                f"Python runtime: {platform.python_version()}\n\n"
                "For detailed CPU/RAM/GPU telemetry, a future version can add dedicated Windows APIs.")
        messagebox.showinfo("System Info", info)

    def open_temp(self):
        import subprocess
        try:
            if os.name == "nt":
                os.startfile(tempfile.gettempdir())
            else:
                messagebox.showinfo(APP_NAME, tempfile.gettempdir())
        except Exception as e:
            messagebox.showerror(APP_NAME, str(e))

    def _finish(self):
        self.busy = False
        self.tweak_btn.configure(state="normal", text="TWEAK")
        self._set_status("DONE — selected tasks completed. Check the log for details.")
        self._log("All selected tasks finished.")
        messagebox.showinfo(APP_NAME, "Finished. Review the log for results and skipped files.")

def main():
    root = tk.Tk()
    NukeTweaker(root)
    root.mainloop()

if __name__ == "__main__":
    main()
