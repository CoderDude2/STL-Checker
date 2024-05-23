from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

import case
import stl
import checks

import os
import shutil

files_path:str = r"C:\Users\TruUser\Desktop\checker\files"
not_centered_path:str = r"C:\Users\TruUser\Desktop\checker\output\not_centered"
over_10_pi_path:str = r"C:\Users\TruUser\Desktop\checker\output\over_10_pi"
over_14_pi_path:str = r"C:\Users\TruUser\Desktop\checker\output\over_14_pi"
passed_path:str = r"C:\Users\TruUser\Desktop\checker\output\passed"
exceeds_max_length_path:str = r"C:\Users\TruUser\Desktop\checker\output\exceeds_max_length"

def main() -> None:
    cases:list[case.Case] = case.get_cases(files_path)
    for c in cases:
        if(not checks.is_centered(c.stl)):
           shutil.move(
                os.path.join(files_path, c.name),
                os.path.join(not_centered_path, c.name)
                ) 
        elif(not c.stl.in_circle_10pi() and c.circle == "10pi"):
            shutil.move(
                os.path.join(files_path, c.name),
                os.path.join(over_10_pi_path, c.name)
                )
        elif(not c.stl.in_circle_14pi() and c.circle == "14pi"):
            shutil.move(
                os.path.join(files_path, c.name),
                os.path.join(over_14_pi_path, c.name)
            )
        elif(c.stl.length() > c.max_length):
            shutil.move(
                os.path.join(files_path, c.name),
                os.path.join(exceeds_max_length_path, c.name)
            )
        else:
            shutil.move(
                os.path.join(files_path, c.name),
                os.path.join(passed_path, c.name)
            )

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
    main()
