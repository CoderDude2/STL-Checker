import tkinter as tk
from tkinter import ttk
import os
import shutil
import threading

import case
import stl
import checks

file_processing_lock = threading.Lock()

OUTPUT_FOLDER_PATH:str = r"C:\Users\TruUser\Desktop\checker\output"
FILES_PATH:str = r"C:\Users\TruUser\Desktop\checker\files"
UNCENTERED_PATH:str = r"C:\Users\TruUser\Desktop\checker\output\uncentered"
OVER_10_PI_PATH:str = r"C:\Users\TruUser\Desktop\checker\output\over_10_pi"
OVER_14_PI_PATH:str = r"C:\Users\TruUser\Desktop\checker\output\over_14_pi"
PASSED_PATH:str = r"C:\Users\TruUser\Desktop\checker\output\passed"
EXCEEDS_MAX_LENGTH_PATH:str = r"C:\Users\TruUser\Desktop\checker\output\exceeds_max_length"

class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("STL Checker")
        self.geometry("250x200")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.processing_thread = threading.Thread(target=self.process_files)
        self.close_event = threading.Event()

        self.uncentered_text:tk.StringVar = tk.StringVar(value="Uncentered: 0")
        self.exceeds_10_pi_text:tk.StringVar = tk.StringVar(value="Exceeds 10pi: 0")
        self.exceeds_14_pi_text:tk.StringVar = tk.StringVar(value="Exceeds 14pi: 0")
        self.exceeds_max_length_text:tk.StringVar = tk.StringVar(value="Exceeds Max Length: 0")
        self.passed_text:tk.StringVar = tk.StringVar(value="Passed: 0")

        self.process_files_btn:tk.Button = tk.Button(text="Process Files", command=self.start_processing)
        self.open_output_btn:tk.Button = tk.Button(text="Open Output Folder", width=20, command=self.open_output_folder)

        self.label_frame:tk.Frame = tk.Frame(master=self)
        self.uncentered_lbl:tk.Label = tk.Label(master=self.label_frame, textvariable=self.uncentered_text)
        self.exceeds_10_pi_lbl:tk.Label = tk.Label(master=self.label_frame, textvariable=self.exceeds_10_pi_text)
        self.exceeds_14_pi_lbl:tk.Label = tk.Label(master=self.label_frame, textvariable=self.exceeds_14_pi_text)
        self.exceeds_max_length_lbl:tk.Label = tk.Label(master=self.label_frame, textvariable=self.exceeds_max_length_text)
        self.passed_lbl:tk.Label = tk.Label(master=self.label_frame, textvariable=self.passed_text)

        self.uncentered_lbl.pack(anchor="w")
        self.exceeds_10_pi_lbl.pack(anchor="w")
        self.exceeds_14_pi_lbl.pack(anchor="w")
        self.exceeds_max_length_lbl.pack(anchor="w")
        self.passed_lbl.pack(anchor="w")

        self.process_files_btn.pack(fill="x")
        
        self.label_frame.pack(fill="x", pady=20)

        self.open_output_btn.pack(fill="x")
    
    def start_processing(self) -> None:
        self.processing_thread.start()

    def process_files(self) -> None:
        with file_processing_lock:
            uncentered_count:int = 0
            exceeds_10pi_count:int = 0
            exceeds_14pi_count:int = 0
            exceeds_max_length_count:int = 0
            passed_count:int = 0

            cases:list[case.Case] = case.get_cases(FILES_PATH)
            
            for c in cases:
                if(not checks.is_centered(c.stl)):
                    shutil.move(
                            os.path.join(FILES_PATH, c.name),
                            os.path.join(UNCENTERED_PATH, c.name)
                            ) 
                    uncentered_count += 1
                    self.uncentered_text.set(f"Uncentered: {uncentered_count}")
                elif(not c.stl.in_circle_10pi() and c.circle == "10pi"):
                    shutil.move(
                        os.path.join(FILES_PATH, c.name),
                        os.path.join(UNCENTERED_PATH, c.name)
                        )
                    exceeds_10pi_count += 1
                    self.uncentered_text.set(f"Exceeds 10pi: {exceeds_10pi_count}")
                elif(not c.stl.in_circle_14pi() and c.circle == "14pi"):
                    shutil.move(
                        os.path.join(FILES_PATH, c.name),
                        os.path.join(UNCENTERED_PATH, c.name)
                    )
                    exceeds_14pi_count += 1
                    self.uncentered_text.set(f"Exceeds 14pi: {exceeds_14pi_count}")
                elif(c.stl.length() > c.max_length):
                    shutil.move(
                        os.path.join(FILES_PATH, c.name),
                        os.path.join(EXCEEDS_MAX_LENGTH_PATH, c.name)
                    )
                    exceeds_max_length_count += 1
                    self.uncentered_text.set(f"Exceeds Max Length: {exceeds_max_length_count}")
                else:
                    shutil.move(
                        os.path.join(FILES_PATH, c.name),
                        os.path.join(PASSED_PATH, c.name)
                    )
                    passed_count += 1
                    self.passed_text.set(f"Passed: {passed_count}")

    def open_output_folder(self) -> None:
        os.startfile(OUTPUT_FOLDER_PATH)

    def on_close(self) -> None:
        self.close_event.set()
        self.destroy()

app = App()
app.mainloop()