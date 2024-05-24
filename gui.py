import tkinter as tk
from tkinter import ttk
import time

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("STL Checker")
        self.geometry("200x200")

        self.process_files_btn = tk.Button(text="Process Files")

        self.uncentered_lbl = tk.Label(text="Uncentered: 0")
        self.exceeds_10_pi_lbl = tk.Label(text="Exceeds 10pi: 0")
        self.exceeds_14_pi_lbl = tk.Label(text="Exceeds 14pi: 0")
        self.exceeds_max_length_lbl = tk.Label(text="Exceeds Max Length: 0")
        self.passed_lbl = tk.Label(text="Passed: 0")

        self.process_files_btn.pack(fill="x")

        self.uncentered_lbl.pack(anchor="w")
        self.exceeds_10_pi_lbl.pack(anchor="w")
        self.exceeds_14_pi_lbl.pack(anchor="w")
        self.exceeds_max_length_lbl.pack(anchor="w")
        self.passed_lbl.pack(anchor="w")

app = App()
app.mainloop()