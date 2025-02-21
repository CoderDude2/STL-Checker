# Author: Isaac J. Boots

from dataclasses import dataclass
from collections import namedtuple
from typing import Generator
from enum import Enum
from pathlib import Path
import re

from stl import STLObject, open_stl_file

class CaseType(Enum):
    DS = 1
    ASC = 2
    TLOC = 3
    AOT = 4

UG = namedtuple('UG', 'UG_101 UG_102 UG_103 UG_104 UG_105', defaults=[None]*5)

case_regex:re.Pattern = re.compile(r"(?P<PDO>\w+-\w+-\d+)__\((?P<connection>[A-Za-z0-9;\-]+),(?P<id>\d+)\) ?\[?(?P<ug_values>[#0-9-=. ]+)?\]?[_0-9]*?(?P<file_type>\.\w+)")
fourteen_millimeter:list[str] = ["NDG-CS", "NDC-CS", "MCN-CS", "MCS-CS", "MCW-CS", "SXR-CS", "SXW-CS", "MRD-CS"]

@dataclass
class Case:
    name:str = ""
    stl:STLObject = None
    pdo:str = ""
    connection:str = ""
    circle_diameter:int = 0
    case_type:CaseType = None
    max_length:float = 0
    ug_values:UG = None

    def __str__(self) -> str:
        return f'{self.pdo} {self.connection}'

def get_cases(folder_path:Path) -> Generator[Case, None, None]:
    if folder_path.exists():
        for file in folder_path.iterdir():
            file_regex_match = case_regex.match(file.name)
            if file.is_file() and file_regex_match and file.suffix.lower() == ".stl":
                abutment_case:Case = Case()

                abutment_case.name = file_regex_match.group(0)
                abutment_case.stl = open_stl_file(file.resolve())
                abutment_case.pdo = file_regex_match.group("PDO")
                abutment_case.connection = file_regex_match.group("connection")

                if("TA10" in file_regex_match.group("connection") or "TC10" in file_regex_match.group("connection")):
                    abutment_case.circle_diameter = 10
                else:
                    abutment_case.circle_diameter = 14
                
                if("T-L" in file_regex_match.group("connection")):
                    abutment_case.case_type = CaseType.TLOC
                elif("AOT" in file_regex_match.group("connection")):
                    abutment_case.case_type = CaseType.AOT
                elif("ASC" in file_regex_match.group("connection")):
                    abutment_case.case_type = CaseType.ASC
                else:
                    abutment_case.case_type = CaseType.DS

                abutment_case.max_length = 14.2 if any([i in file_regex_match.group("connection") for i in fourteen_millimeter]) else 17.2

                val_101:float = None
                val_102:float = None
                val_103:float = None
                val_104:float = None
                val_105:float = None

                if file_regex_match.group("ug_values") is not None:
                    for ug_value_entry in file_regex_match.group("ug_values").split(" "):
                        ug_value:list[str] = ug_value_entry.split("=")
                        match ug_value[0]:
                            case "#101":
                                try:
                                    val_101 = float(ug_value[1])
                                except ValueError:
                                    val_101 = None
                            case "#102":
                                try:
                                    val_102 = float(ug_value[1])
                                except ValueError:
                                    val_102 = None
                            case "#103":
                                try:
                                    val_103 = float(ug_value[1])
                                except ValueError:
                                    val_103 = None
                            case "#104":
                                try:
                                    val_104 = float(ug_value[1])
                                except ValueError:
                                    val_104 = None
                            case "#105":
                                try:
                                    val_105 = float(ug_value[1])
                                except ValueError:
                                    val_105 = None
                    abutment_case.ug_values = UG(val_101, val_102, val_103, val_104, val_105)
                yield abutment_case

if __name__ == "__main__":
    abutments = get_cases(Path("./files"))
    for abutment in abutments:
        print(abutment.name)
        print(f'facet count: {abutment.stl.facet_count}')
        print(abutment.pdo)
        print(abutment.connection)
        print(abutment.circle_diameter)
        print(abutment.case_type)
        print(abutment.max_length)
        print(abutment.ug_values)
        print()