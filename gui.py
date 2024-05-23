import tkinter as tk
from tkinter import ttk
import time

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("STL Checker")
        self.geometry("200x200")

        self.process_files_btn = tk.Button(text="Process Files")


app = App()
app.mainloop()