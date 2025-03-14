# Author: Isaac J. Boots

from dataclasses import dataclass
from typing import NamedTuple
from typing import Generator, Optional
from enum import Enum
from pathlib import Path
import re

from stl import STLObject, open_stl_file


class AbutmentType(Enum):
    DS = 1
    ASC = 2
    TLOC = 3
    AOT = 4


class UG(NamedTuple):
    UG_101: float | None = None
    UG_102: float | None = None
    UG_103: float | None = None
    UG_104: float | None = None
    UG_105: float | None = None


case_regex: re.Pattern = re.compile(
    r"(?P<PDO>\w+-\w+-\d+)__\((?P<connection>[A-Za-z0-9;\-]+),(?P<id>\d+)\) ?\[?(?P<ug_values>[#0-9-=. ]+)?\]?[_0-9]*?(?P<file_type>\.\w+)"
)
fourteen_millimeter: list[str] = [
    "NDG-CS",
    "NDC-CS",
    "MCN-CS",
    "MCS-CS",
    "MCW-CS",
    "SXR-CS",
    "SXW-CS",
    "MRD-CS",
]


@dataclass
class Abutment:
    name: str = ""
    stl: Optional[STLObject] = None
    pdo: str = ""
    connection: str = ""
    circle_diameter: int = 0
    abutment_type: Optional[AbutmentType] = None
    max_length: float = 0
    ug_values: Optional[UG] = None
    is_special: bool = False

    def __str__(self) -> str:
        return f"{self.pdo} {self.connection}"


def get_abutments(folder_path: Path) -> Generator[Abutment, None, None]:
    if folder_path.exists():
        for file in folder_path.iterdir():
            file_regex_match = case_regex.match(file.name)
            if file.is_file() and file_regex_match and file.suffix.lower() == ".stl":
                abutment: Abutment = Abutment()

                abutment.name = file_regex_match.group(0)
                abutment.stl = open_stl_file(str(file.resolve()))
                abutment.pdo = file_regex_match.group("PDO")
                abutment.connection = file_regex_match.group("connection")

                if "TA10" in file_regex_match.group(
                    "connection"
                ) or "TC10" in file_regex_match.group("connection"):
                    abutment.circle_diameter = 10
                else:
                    abutment.circle_diameter = 14

                if "T-L" in file_regex_match.group("connection"):
                    abutment.abutment_type = AbutmentType.TLOC
                    abutment.is_special = True
                elif "AOT" in file_regex_match.group("connection"):
                    abutment.abutment_type = AbutmentType.AOT
                    abutment.is_special = True
                elif "ASC" in file_regex_match.group("connection"):
                    abutment.abutment_type = AbutmentType.ASC
                    abutment.is_special = True
                else:
                    abutment.abutment_type = AbutmentType.DS

                if file_regex_match.group("connection") in fourteen_millimeter:
                    abutment.max_length = 14.2
                else:
                    abutment.max_length = 17.2

                if file_regex_match.group("ug_values") is not None:
                    val_101: Optional[float] = None
                    val_102: Optional[float] = None
                    val_103: Optional[float] = None
                    val_104: Optional[float] = None
                    val_105: Optional[float] = None

                    for ug_value_entry in file_regex_match.group("ug_values").split(
                        " "
                    ):
                        ug_value: list[str] = ug_value_entry.split("=")
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
                    abutment.ug_values = UG(val_101, val_102, val_103, val_104, val_105)
                yield abutment


if __name__ == "__main__":
    abutments = get_abutments(Path("./files"))
    for abutment in abutments:
        print(abutment.name)
        if abutment.stl:
            print(f"facet count: {abutment.stl.facet_count}")
        print(abutment.pdo)
        print(abutment.connection)
        print(abutment.circle_diameter)
        print(abutment.abutment_type)
        print(abutment.max_length)
        print(abutment.ug_values)
        print()
