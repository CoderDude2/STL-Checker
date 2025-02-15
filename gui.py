# Author: Isaac J. Boots

import os
import shutil
import threading
import tkinter as tk
from pathlib import Path

import case
from case import CaseType
import checks


ROOT_DIR = Path(__file__).resolve().parent

OUTPUT_FOLDER_PATH:str = os.path.join(ROOT_DIR, "output")
FILES_PATH:str = os.path.join(ROOT_DIR, "files")
UNCENTERED_PATH:str = os.path.join(ROOT_DIR, "output/uncentered")
OVER_10_PI_PATH:str = os.path.join(ROOT_DIR, "output/over_10_pi")
OVER_14_PI_PATH:str = os.path.join(ROOT_DIR, "output/over_14_pi")
EXCEEDS_MAX_LENGTH_PATH:str = os.path.join(ROOT_DIR, "output/exceeds_max_length")
MISSING_UG_VALUES_PATH:str = os.path.join(ROOT_DIR, "output/missing_ug_values")
INCORRECT_104_VALUE_PATH:str = os.path.join(ROOT_DIR, "output/incorrect_104_value")
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

if(not os.path.exists(MISSING_UG_VALUES_PATH)):
    os.mkdir(MISSING_UG_VALUES_PATH)

if(not os.path.exists(INCORRECT_104_VALUE_PATH)):
    os.mkdir(INCORRECT_104_VALUE_PATH)

if(not os.path.exists(PASSED_PATH)):
    os.mkdir(PASSED_PATH)

file_processing_lock:threading.Lock = threading.Lock()

class Checker(threading.Thread):
    def __init__(self, gui_app) -> None:
        threading.Thread.__init__(self, daemon=True)
        self.is_checking:bool = False
        self.gui_app = gui_app

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
                            continue

                        if checks.in_circle(c.stl, 7):
                            if(c.circle == "10pi" and not checks.in_circle(c.stl, 5)):
                                shutil.move(
                                    os.path.join(FILES_PATH, c.name),
                                    os.path.join(OVER_10_PI_PATH, c.name)
                                )
                                continue
                        else:
                            shutil.move(
                                os.path.join(FILES_PATH, c.name),
                                os.path.join(OVER_14_PI_PATH, c.name)
                            )
                            continue  

                        if(c.stl.length() > c.max_length):
                            shutil.move(
                                os.path.join(FILES_PATH, c.name),
                                os.path.join(EXCEEDS_MAX_LENGTH_PATH, c.name)
                            )
                            continue

                        if(c.case_type == CaseType.ASC and c.ug_values == None):
                            shutil.move(
                                os.path.join(FILES_PATH, c.name),
                                os.path.join(MISSING_UG_VALUES_PATH, c.name)
                            )
                            continue

                        if(c.case_type == CaseType.TLOC or c.case_type == CaseType.AOT):
                            if c.ug_values == "":
                                continue
                            elif c.ug_values == None:
                                shutil.move(
                                    os.path.join(FILES_PATH, c.name),
                                    os.path.join(MISSING_UG_VALUES_PATH, c.name)
                                )
                                continue
                            else:
                                if(c.ug_values["#102"] <= 5 and c.ug_values["#104"] != 0):
                                    shutil.move(
                                    os.path.join(FILES_PATH, c.name),
                                    os.path.join(INCORRECT_104_VALUE_PATH, c.name)
                                )
                                continue
                        shutil.move(os.path.join(FILES_PATH, c.name),os.path.join(PASSED_PATH, c.name))
                    except FileNotFoundError:
                        print("Could not find file", c.name)
                self.is_checking = False
                self.gui_app.done_processing_callback()

class App:
    def __init__(self) -> None:
        self.master:tk.Tk = tk.Tk()
        self.master.iconbitmap(os.path.join(ROOT_DIR, "resources", "icon.ico"))
        self.master.title("STL Checker")
        self.master.option_add("*Font", "Arial 11")
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        self.master.config(background="#dddddd")
        self.master.geometry("250x404")
        self.master.minsize(250,250)

        self.update_counters_thread = threading.Thread(target=self.update_counters, daemon=True)

        self.c:Checker = Checker(self)
        self.c.start()
        self.update_counters_thread.start()

        self.uncentered_counter:tk.IntVar = tk.IntVar(value=0)
        self.exceeds_10_pi_counter:tk.IntVar = tk.IntVar(value=0)
        self.exceeds_14_pi_counter:tk.IntVar = tk.IntVar(value=0)
        self.exceeds_max_length_counter:tk.IntVar = tk.IntVar(value=0)
        self.missing_ug_values_counter:tk.IntVar = tk.IntVar(value=0)
        self.incorrect_104_value_counter:tk.IntVar = tk.IntVar(value=0)
        self.passed_counter:tk.IntVar = tk.IntVar(value=0)

        self.add_files_btn:tk.Button = tk.Button(text="Add Files", command=self.open_files_folder)
        self.process_files_btn:tk.Button = tk.Button(text="Process Files", command=self.start_processing_callback)
        self.open_output_btn:tk.Button = tk.Button(text="Open Output Folder", width=20, command=self.open_output_folder)

        self.label_frame:tk.Frame = tk.Frame(master=self.master)
        self.label_frame.option_add("*Label.Background", "#dddddd")
        self.label_frame.grid_rowconfigure(list(range(7)), weight=1, uniform="Silent_Creme")
        self.label_frame.grid_columnconfigure(0, weight=1)
        self.spacer_frame:tk.Frame = tk.Frame(master=self.label_frame, width=20)

        self.uncentered_lbl:tk.Label = tk.Label(master=self.label_frame, text="Uncentered", anchor="w")
        self.uncentered_count_lbl:tk.Label = tk.Label(master=self.label_frame, textvariable=self.uncentered_counter, width=5)

        self.exceeds_10_pi_lbl:tk.Label = tk.Label(master=self.label_frame, text="Exceeds 10pi", anchor="w")
        self.exceeds_10_pi_count_lbl:tk.Label = tk.Label(master=self.label_frame, textvariable=self.exceeds_10_pi_counter)

        self.exceeds_14_pi_lbl:tk.Label = tk.Label(master=self.label_frame, text="Exceeds 14pi", anchor="w")
        self.exceeds_14_pi_count_lbl:tk.Label = tk.Label(master=self.label_frame, textvariable=self.exceeds_14_pi_counter)

        self.exceeds_max_length_lbl:tk.Label = tk.Label(master=self.label_frame, text="Exceeds Max Length", anchor="w")
        self.exceeds_max_length_count_lbl:tk.Label = tk.Label(master=self.label_frame, textvariable=self.exceeds_max_length_counter)

        self.missing_ug_values_lbl:tk.Label = tk.Label(master=self.label_frame, text="Missing UG Values", anchor="w")
        self.missing_ug_values_count_lbl:tk.Label = tk.Label(master=self.label_frame, textvariable=self.missing_ug_values_counter)

        self.incorrect_104_value_lbl:tk.Label = tk.Label(master=self.label_frame, text="Incorrect 104 Value", anchor="w")
        self.incorrect_104_value_count_lbl:tk.Label = tk.Label(master=self.label_frame, textvariable=self.incorrect_104_value_counter)

        self.passed_lbl:tk.Label = tk.Label(master=self.label_frame, text="Passed", anchor="w")
        self.passed_count_lbl:tk.Label = tk.Label(master=self.label_frame, textvariable=self.passed_counter)

        self.uncentered_lbl.grid(row=0, column=0, sticky="nsew")
        self.uncentered_count_lbl.grid(row=0, column=1, sticky="nsew")

        self.exceeds_10_pi_lbl.grid(row=1, column=0, sticky="nsew")
        self.exceeds_10_pi_count_lbl.grid(row=1, column=1, sticky="nsew")

        self.exceeds_14_pi_lbl.grid(row=2, column=0, sticky="nsew")
        self.exceeds_14_pi_count_lbl.grid(row=2, column=1, sticky="nsew")

        self.exceeds_max_length_lbl.grid(row=3, column=0, sticky="nsew")
        self.exceeds_max_length_count_lbl.grid(row=3, column=1, sticky="nsew")

        self.missing_ug_values_lbl.grid(row=4, column=0, sticky="nsew")
        self.missing_ug_values_count_lbl.grid(row=4, column=1, sticky="nsew")

        self.incorrect_104_value_lbl.grid(row=5, column=0, sticky="nsew")
        self.incorrect_104_value_count_lbl.grid(row=5, column=1, sticky="nsew")

        self.passed_lbl.grid(row=6, column=0, sticky="nsew")
        self.passed_count_lbl.grid(row=6, column=1, sticky="nsew")

        self.master.grid_rowconfigure(2, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        self.add_files_btn.grid(row=0, column=0, sticky="we")
        self.process_files_btn.grid(row=1, column=0, sticky="we")
        self.label_frame.grid(row=2, column=0, sticky="nswe", padx=5)
        self.open_output_btn.grid(row=3, column=0, sticky="we")

    def start_processing_callback(self):
        if len(os.listdir(FILES_PATH)) > 0:
            self.master.config(cursor="watch")
            self.master.title("STL-Checker (Processing)")
            self.process_files_btn.config(state=tk.DISABLED, text="Processing...")
            self.c.start_processing()

    def done_processing_callback(self):
        self.master.config(cursor="")
        self.process_files_btn.config(state=tk.NORMAL, text="Process Files")
        self.master.title("STL-Checker")

    def update_counters(self) -> None:
        prev_uncentered_count = 0
        prev_exceeds_10pi_count = 0
        prev_exceeds_14pi_count = 0
        prev_exceeds_length_count = 0
        prev_missing_ug_values_count = 0
        prev_incorrect_104_value_count = 0
        prev_passed_count = 0

        while True:
            uncentered_count = len([file for file in os.listdir(UNCENTERED_PATH) if ".stl" in file.lower()])
            exceeds_10pi_count = len([file for file in os.listdir(OVER_10_PI_PATH) if ".stl" in file.lower()])
            exceeds_14pi_count = len([file for file in os.listdir(OVER_14_PI_PATH) if ".stl" in file.lower()])
            exceeds_length_count = len([file for file in os.listdir(EXCEEDS_MAX_LENGTH_PATH) if ".stl" in file.lower()])
            missing_ug_values_count = len([file for file in os.listdir(MISSING_UG_VALUES_PATH) if ".stl" in file.lower()])
            incorrect_104_value_count = len([file for file in os.listdir(INCORRECT_104_VALUE_PATH) if ".stl" in file.lower()])
            passed_count = len([file for file in os.listdir(PASSED_PATH) if ".stl" in file.lower()])

            if uncentered_count != prev_uncentered_count:
                prev_uncentered_count = uncentered_count
                self.uncentered_counter.set(uncentered_count)
            
            if exceeds_10pi_count != prev_exceeds_10pi_count:
                prev_exceeds_10pi_count = exceeds_10pi_count
                self.exceeds_10_pi_counter.set(exceeds_10pi_count)
            
            if exceeds_14pi_count != prev_exceeds_14pi_count:
                prev_exceeds_14pi_count = exceeds_14pi_count
                self.exceeds_14_pi_counter.set(exceeds_14pi_count)
            
            if exceeds_length_count != prev_exceeds_length_count:
                prev_exceeds_length_count = exceeds_length_count
                self.exceeds_max_length_counter.set(exceeds_length_count)
            
            if missing_ug_values_count != prev_missing_ug_values_count:
                prev_missing_ug_values_count = missing_ug_values_count
                self.missing_ug_values_counter.set(missing_ug_values_count)

            if incorrect_104_value_count != prev_incorrect_104_value_count:
                prev_incorrect_104_value_count = incorrect_104_value_count
                self.incorrect_104_value_counter.set(incorrect_104_value_count)

            if passed_count != prev_passed_count:
                prev_passed_count = passed_count
                self.passed_counter.set(passed_count)

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