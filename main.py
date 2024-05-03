import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt

import case
import stl

def main() -> None:
    cases:list[case.Case] = case.get_cases("stls")

if __name__ == "__main__":
    main()
