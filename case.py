from dataclasses import dataclass
import os
import re

import stl

case_regex:re.Pattern = re.compile(r"(?P<PDO>\w+-\w+-\d+)__\((?P<connection_type>[A-Za-z0-9;\-]+),(?P<id>\d+)\)\[?(?P<angle>[A-Za-z0-9\.\-#= ]+)?\]?(?P<file_type>\.\w+)")
fourteen_millimeter = ["NDG-CS", "NDC-CS", "MCN-CS", "MCS-CS", "MCW-CS", "SXR-CS", "SXW-CS", "MRD-CS"]

@dataclass
class Case:
    stl:stl.STLObject
    pdo:str
    connection:str
    circle:str
    case_type:str
    max_length:float

    def __str__(self) -> str:
        return f'{self.pdo} {self.connection}'

def get_cases(folder_path:str) -> list[Case]:
    cases:list[Case] = []
    for file in os.listdir(folder_path):
        file_name = case_regex.match(file)
        if(file_name):
            stl_file:stl.STLObject = stl.open_stl_file(os.path.join(folder_path, file_name.group(0)))
            circle:str = ""
            case_type:str = ""
            max_length:float = 14.2 if any([i in file_name.group("connection_type") for i in fourteen_millimeter]) else 17.2

            if("TA14" in file_name.group("connection_type")):
                circle = "14pi"
            elif("TA10" in file_name.group("connection_type")):
                circle = "10pi"
            else:
                circle = "14pi"

            if("T-L" in file_name.group("connection_type")):
                case_type = "TLOC"
            elif("AOT" in file_name.group("connection_type")):
                case_type = "AOT"
            elif("ASC" in file_name.group("connection_type")):
                case_type = "ASC"
            else:
                case_type = "DS"

            c:Case = Case(stl_file, file_name.group("PDO"), file_name.group("connection_type"), circle, case_type, max_length)
            cases.append(c)
    return cases
        
            
