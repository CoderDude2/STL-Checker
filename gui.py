# Author: Isaac J. Boots

import os
import shutil
import threading
import tkinter as tk
from pathlib import Path
import time

import case
import checks


ROOT_DIR = Path(__file__).resolve().parent

OUTPUT_FOLDER_PATH:str = os.path.join(ROOT_DIR, "output")
FILES_PATH:str = os.path.join(ROOT_DIR, "files")
UNCENTERED_PATH:str = os.path.join(ROOT_DIR, "output/uncentered")
OVER_10_PI_PATH:str = os.path.join(ROOT_DIR, "output/over_10_pi")
OVER_14_PI_PATH:str = os.path.join(ROOT_DIR, "output/over_14_pi")
EXCEEDS_MAX_LENGTH_PATH:str = os.path.join(ROOT_DIR, "output/exceeds_max_length")
PASSED_PATH:str = os.path.join(ROOT_DIR, "output/passed")

if(not os.path.exists(OUTPUT_FOLDER_PATH)):
    os.mkdir(OUTPUT_FOLDER_PATH)

if(not os.path.exists(FILES_PATH)):
    os.mkdir(FILES_PATH)

if(not os.path.exists(UNCENTERED_PATH)):
    os.mkdir(UNCENTERED_PATH)

if(not os.path.exists(OVER_10_PI_PATH)):
    os.mkdir(OVER_10_PI_PATH)

if(not os.path.exists(OVER_14_PI_PATH)):
    os.mkdir(OVER_14_PI_PATH)

if(not os.path.exists(EXCEEDS_MAX_LENGTH_PATH)):
    os.mkdir(EXCEEDS_MAX_LENGTH_PATH)

if(not os.path.exists(PASSED_PATH)):
    os.mkdir(PASSED_PATH)

file_processing_lock:threading.Lock = threading.Lock()

class Checker(threading.Thread):
    def __init__(self) -> None:
        threading.Thread.__init__(self, daemon=True)
        self.is_checking:bool = False

    def run(self) -> None:
        while True:
            self.process_files()

    def start_processing(self) -> None:
        self.is_checking = True if self.is_checking == False else self.is_checking
        
    def process_files(self) -> None:
        if(self.is_checking):
            with file_processing_lock:
                cases:list[case.Case] = case.get_cases(FILES_PATH)
                
                for c in cases:
                    try:
                        if(not checks.is_centered(c.stl)):
                            shutil.move(
                                    os.path.join(FILES_PATH, c.name),
                                    os.path.join(UNCENTERED_PATH, c.name)
                                    ) 
                        elif(not c.stl.in_circle_10pi() and c.circle == "10pi"):
                            shutil.move(
                                os.path.join(FILES_PATH, c.name),
                                os.path.join(OVER_10_PI_PATH, c.name)
                                )
                        elif(not c.stl.in_circle_14pi() and c.circle == "14pi"):
                            shutil.move(
                                os.path.join(FILES_PATH, c.name),
                                os.path.join(OVER_14_PI_PATH, c.name)
                            )
                        elif(c.stl.length() > c.max_length):
                            shutil.move(
                                os.path.join(FILES_PATH, c.name),
                                os.path.join(EXCEEDS_MAX_LENGTH_PATH, c.name)
                            )
                        else:
                            shutil.move(
                                os.path.join(FILES_PATH, c.name),
                                os.path.join(PASSED_PATH, c.name)
                            )
                    except FileNotFoundError:
                        print("Could not find file", c.name)
                self.is_checking = False

class App:
    def __init__(self) -> None:
        self.master:tk.Tk = tk.Tk()
        self.master.iconbitmap(os.path.join(ROOT_DIR, "resources", "icon.ico"))
        self.master.title("STL Checker")
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

        self.update_counters_thread = threading.Thread(target=self.update_counters, daemon=True)

        self.c:Checker = Checker()
        self.c.start()
        self.update_counters_thread.start()

        self.uncentered_text:tk.StringVar = tk.StringVar(value="Uncentered: 0")
        self.exceeds_10_pi_text:tk.StringVar = tk.StringVar(value="Exceeds 10pi: 0")
        self.exceeds_14_pi_text:tk.StringVar = tk.StringVar(value="Exceeds 14pi: 0")
        self.exceeds_max_length_text:tk.StringVar = tk.StringVar(value="Exceeds Max Length: 0")
        self.passed_text:tk.StringVar = tk.StringVar(value="Passed: 0")

        self.add_files_btn:tk.Button = tk.Button(text="Add Files", command=self.open_files_folder)
        self.process_files_btn:tk.Button = tk.Button(text="Process Files", command=self.c.start_processing)
        self.open_output_btn:tk.Button = tk.Button(text="Open Output Folder", width=20, command=self.open_output_folder)

        self.label_frame:tk.Frame = tk.Frame(master=self.master)
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

        self.add_files_btn.pack(fill="x")
        self.process_files_btn.pack(fill="x")
        self.label_frame.pack(fill="x", pady=20)
        self.open_output_btn.pack(fill="x", side=tk.BOTTOM)


    def update_counters(self) -> None:
        prev_uncentered_count = 0
        prev_exceeds_10pi_count = 0
        prev_exceeds_14pi_count = 0
        prev_exceeds_length_count = 0
        prev_passed_count = 0

        while True:
            uncentered_count = len([file for file in os.listdir(UNCENTERED_PATH) if ".stl" in file.lower()])
            exceeds_10pi_count = len([file for file in os.listdir(OVER_10_PI_PATH) if ".stl" in file.lower()])
            exceeds_14pi_count = len([file for file in os.listdir(OVER_14_PI_PATH) if ".stl" in file.lower()])
            exceeds_length_count = len([file for file in os.listdir(EXCEEDS_MAX_LENGTH_PATH) if ".stl" in file.lower()])
            passed_count = len([file for file in os.listdir(PASSED_PATH) if ".stl" in file.lower()])

            if uncentered_count != prev_uncentered_count:
                prev_uncentered_count = uncentered_count
                self.uncentered_text.set(f"Uncentered: {uncentered_count}")
            
            if exceeds_10pi_count != prev_exceeds_10pi_count:
                prev_exceeds_10pi_count = exceeds_10pi_count
                self.exceeds_10_pi_text.set(f"Exceeds 10pi: {exceeds_10pi_count}")
            
            if exceeds_14pi_count != prev_exceeds_14pi_count:
                prev_exceeds_14pi_count = exceeds_14pi_count
                self.exceeds_14_pi_text.set(f"Exceeds 14pi: {exceeds_14pi_count}")
            
            if exceeds_length_count != prev_exceeds_length_count:
                prev_exceeds_length_count = exceeds_length_count
                self.exceeds_max_length_text.set(f"Exceeds Max Length: {exceeds_length_count}")
            
            if passed_count != prev_passed_count:
                prev_passed_count = passed_count
                self.passed_text.set(f"Passed: {passed_count}")

    def open_files_folder(self) -> None:
        if(os.name == "nt"):
            os.system(f'start {FILES_PATH}')
        else:
            os.system(f'open {FILES_PATH}')

    def open_output_folder(self) -> None:
        if(os.name == "nt"):
            os.system(f'start {OUTPUT_FOLDER_PATH}')
        else:
            os.system(f'open {OUTPUT_FOLDER_PATH}')
        

    def run(self) -> None:
        self.master.mainloop()

    def on_close(self) -> None:
        self.master.quit()