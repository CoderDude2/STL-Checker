# Author: Isaac J. Boots

from dataclasses import dataclass
from enum import Enum
import os
import re

import stl

CaseType = Enum('CaseType', names=[
    "DS",
    "ASC",
    "TLOC",
    "AOT"
])

case_regex:re.Pattern = re.compile(r"(?P<PDO>\w+-\w+-\d+)__\((?P<connection_type>[A-Za-z0-9;\-]+),(?P<id>\d+)\)\[?(?P<ug_values>[A-Za-z0-9\.\-#= ]+)?\]?(?P<file_type>\.\w+)")
fourteen_millimeter:list[str] = ["NDG-CS", "NDC-CS", "MCN-CS", "MCS-CS", "MCW-CS", "SXR-CS", "SXW-CS", "MRD-CS"]

@dataclass
class Case:
    name:str
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
    if(os.path.exists(folder_path)):
        for file in os.listdir(folder_path):
            file_name = case_regex.match(file)
            if(file_name and file_name.group('file_type') == '.stl'):
                name:str=file_name.group(0)
                stl_file:stl.STLObject = stl.open_stl_file(os.path.join(folder_path, file_name.group(0)))
                circle:str = ""
                case_type:str = ""
                max_length:float = 14.2 if any([i in file_name.group("connection_type") for i in fourteen_millimeter]) else 17.2

                if("TA14" in file_name.group("connection_type") or "TC14" in file_name.group("connection_type")):
                    circle = "14pi"
                elif("TA10" in file_name.group("connection_type") or "TC10" in file_name.group("connection_type")):
                    circle = "10pi"
                else:
                    circle = "14pi"

                if("T-L" in file_name.group("connection_type")):
                    case_type = CaseType.TLOC
                elif("AOT" in file_name.group("connection_type")):
                    case_type = CaseType.AOT
                elif("ASC" in file_name.group("connection_type")):
                    case_type = CaseType.ASC
                else:
                    case_type = CaseType.ASC

                c:Case = Case(name, stl_file, file_name.group("PDO"), file_name.group("connection_type"), circle, case_type, max_length)
                cases.append(c)
    return cases