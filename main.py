import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt

import case
import stl

def main() -> None:
    cases:list[case.Case] = case.get_cases("stls")
    for c in cases:
        if(c.stl.length() > c.max_length):
            print(f"{c} length exceeds max length of {c.max_length}\nActual Length: {c.stl.length()}")
        if(not c.stl.in_circle_10pi() and c.circle == "10pi"):
            print(c, "Exceeds 10pi!")
        elif(not c.stl.in_circle_14pi() and c.circle == "14pi"):
            print(c, "Exceeds 14pi!")
        else:
            print(c, c.stl.length(), c.max_length)

if __name__ == "__main__":
    main()
