import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np


import case
import stl
import checks
import time

def main() -> None:
    cases:list[case.Case] = case.get_cases("stls")
    for c in cases:
        if(not c.stl.in_circle_10pi() and c.circle == "10pi"):
            print(c, "Exceeds 10pi!")
        if(not c.stl.in_circle_14pi() and c.circle == "14pi"):
            print(c, "Exceeds 14pi!")
        print(c, c.stl.length(), c.max_length)

        start = time.perf_counter()
        print("Centered:", checks.is_centered(c.stl))
        end = time.perf_counter()
        print(round(end - start, 5), "Seconds")
        print()

def graph(stl_file:stl.STLObject) -> None:
    x:list[float] = []
    y:list[float] = []
    z:list[float] = []

    for facet in stl_file.facets:
        x.append(facet.v1[0])
        y.append(facet.v1[1])
        z.append(facet.v1[2])

        x.append(facet.v2[0])
        y.append(facet.v2[1])
        z.append(facet.v2[2])

        x.append(facet.v3[0])
        y.append(facet.v3[1])
        z.append(facet.v3[2])

    fig:plt.Figure = plt.figure()
    ax:plt.Axes = fig.add_subplot(111, projection='3d')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    theta = np.linspace(0, 2*np.pi, 360)
    y1 = 5*np.cos(theta)
    z1 = 5*np.sin(theta)

    y2 = 7*np.cos(theta)
    z2 = 7*np.sin(theta)

    ax.plot(y1,z1)
    ax.plot(y2,z2)
    ax.plot(x,y,z, 'o')

    ax.plot(0,0,0,'o')

    plt.show()


if __name__ == "__main__":
    graph(stl.open_stl_file("stls/PDO-PL-0251664__(MRD-CS-TA10,1664).stl"))
    main()
