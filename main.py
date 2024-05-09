import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt

import case
import stl

def main() -> None:
    cases:list[case.Case] = case.get_cases("stl")
    for c in cases:
        # if(c.stl.length() > c.max_length):
        #     print(f"{c} length exceeds max length of {c.max_length}\nActual Length: {c.stl.length()}")
        if(not c.stl.in_circle_10pi() and c.circle == "10pi"):
            print(c, "Exceeds 10pi!")
        if(not c.stl.in_circle_14pi() and c.circle == "14pi"):
            print(c, "Exceeds 14pi!")
        print(c, c.stl.length(), c.max_length)
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
    ax.plot(x,y,z,'o')

    plt.show()


if __name__ == "__main__":
    main()
