# Author: Isaac J. Boots

import os
import shutil
import threading
import tkinter as tk
from pathlib import Path
from multiprocessing import Pool

from abutment import AbutmentType, Abutment, get_abutments
import checks


ROOT_DIR = Path(__file__).resolve().parent

OUTPUT_FOLDER_PATH = ROOT_DIR.joinpath("output")
FILES_PATH = ROOT_DIR.joinpath("files")

UNCENTERED_PATH = OUTPUT_FOLDER_PATH.joinpath("uncentered")
OVER_10_PI_PATH = OUTPUT_FOLDER_PATH.joinpath("over_10_pi")
OVER_14_PI_PATH = OUTPUT_FOLDER_PATH.joinpath("over_14_pi")
EXCEEDS_MAX_LENGTH_PATH = OUTPUT_FOLDER_PATH.joinpath("exceeds_max_length")
MISSING_UG_VALUES_PATH = OUTPUT_FOLDER_PATH.joinpath("missing_ug_values")
INCORRECT_104_VALUE_PATH= OUTPUT_FOLDER_PATH.joinpath("incorrect_104_value")
PASSED_PATH = OUTPUT_FOLDER_PATH.joinpath("passed")


if not OUTPUT_FOLDER_PATH.exists():
    OUTPUT_FOLDER_PATH.mkdir()

if not FILES_PATH.exists():
    FILES_PATH.mkdir()

if not UNCENTERED_PATH.exists():
    UNCENTERED_PATH.mkdir()

if not OVER_10_PI_PATH.exists():
    OVER_10_PI_PATH.mkdir()

if not OVER_14_PI_PATH.exists():
    OVER_14_PI_PATH.mkdir()

if not EXCEEDS_MAX_LENGTH_PATH.exists():
    EXCEEDS_MAX_LENGTH_PATH.mkdir()

if not MISSING_UG_VALUES_PATH.exists():
    MISSING_UG_VALUES_PATH.mkdir()

if not INCORRECT_104_VALUE_PATH.exists():
    INCORRECT_104_VALUE_PATH.mkdir()

if not PASSED_PATH.exists():
    PASSED_PATH.mkdir()
        
def process_file(abutment:Abutment) -> None:
    src = FILES_PATH.joinpath(abutment.name)
    dst = PASSED_PATH.joinpath(abutment.name)
    try:
        if not checks.is_centered(abutment.stl):
            dst = UNCENTERED_PATH.joinpath(abutment.name)
            return (src, dst)
        
        if not checks.in_circle(abutment.stl, 7):
            dst = OVER_14_PI_PATH.joinpath(abutment.name)
            return (src, dst)
        
        if not checks.in_circle(abutment.stl, 5) and abutment.circle_diameter == 10:
            dst = OVER_10_PI_PATH.joinpath(abutment.name)
            return (src, dst)
        
        if abutment.stl.length() > abutment.max_length:
            dst = EXCEEDS_MAX_LENGTH_PATH.joinpath(abutment.name)
            return (src, dst)
        
        if abutment.is_special and abutment.ug_values is None:
            dst = MISSING_UG_VALUES_PATH.joinpath(abutment.name)
            return (src, dst)

        if (abutment.abutment_type == AbutmentType.TLOC or abutment.abutment_type == AbutmentType.AOT) and abutment.ug_values.UG_102 <= 5 and abutment.ug_values.UG_104 != 0:
            dst = INCORRECT_104_VALUE_PATH.joinpath(abutment.name)
            return (src, dst)        
        return (src, dst)
    except FileNotFoundError:
        print("Could not find file", abutment.name)

def process_files(gui_app):
    with Pool() as pool:
        result = pool.imap_unordered(process_file, get_abutments(FILES_PATH))

        for src, dst in result:
            shutil.move(src, dst)
    gui_app.done_processing_callback()
    
    return

class App:
    def __init__(self) -> None:
        self.master:tk.Tk = tk.Tk()
        self.master.iconbitmap(Path(ROOT_DIR, "resources", "icon.ico"))
        self.master.title("STL-Checker")
        self.master.option_add("*Font", "Arial 11")
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        self.master.config(background="#dddddd")
        self.master.geometry("250x404")
        self.master.minsize(250,250)

        self.update_counters_thread = threading.Thread(target=self.update_counters, daemon=True)
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
        self.master.config(cursor="watch")
        self.master.title("STL-Checker (Processing)")
        self.process_files_btn.config(state=tk.DISABLED, text="Processing...")

        t = threading.Thread(target=process_files, args=(self, ))
        t.setDaemon(True)
        t.start()

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
            uncentered_count = len([file for file in UNCENTERED_PATH.iterdir() if file.suffix.lower() == ".stl"])
            exceeds_10pi_count = len([file for file in OVER_10_PI_PATH.iterdir() if file.suffix.lower() == ".stl"])
            exceeds_14pi_count = len([file for file in OVER_14_PI_PATH.iterdir() if file.suffix.lower() == ".stl"])
            exceeds_length_count = len([file for file in EXCEEDS_MAX_LENGTH_PATH.iterdir() if file.suffix.lower() == ".stl"])
            missing_ug_values_count = len([file for file in MISSING_UG_VALUES_PATH.iterdir() if file.suffix.lower() == ".stl"])
            incorrect_104_value_count = len([file for file in INCORRECT_104_VALUE_PATH.iterdir() if file.suffix.lower() == ".stl"])
            passed_count = len([file for file in PASSED_PATH.iterdir() if file.suffix.lower() == ".stl"])

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
        if os.name == "nt":
            os.system(f'start {FILES_PATH}')
        else:
            os.system(f'open {FILES_PATH}')

    def open_output_folder(self) -> None:
        if os.name == "nt":
            os.system(f'start {OUTPUT_FOLDER_PATH}')
        else:
            os.system(f'open {OUTPUT_FOLDER_PATH}')
        

    def run(self) -> None:
        self.master.mainloop()

    def on_close(self) -> None:
        self.master.quit()