import stl
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.patches import Circle

def main() -> None:
    stl_file = stl.open_stl_file("test.stl")
    print(stl_file.in_circle_10pi())

    x = []
    y = []
    z = []

    for facet in stl_file.facets:
        x.append(facet.v1[0])
        y.append(facet.v1[1])
        z.append(facet.v1[2])

        x.append(facet.v2[0])
        y.append(facet.v2[1])
        z.append(facet.v2[2])

        x.append(facet.v2[0])
        y.append(facet.v2[1])
        z.append(facet.v2[2])

    # for i in zip(x,y):
    #     distance = stl.distance_from_origin(np.array(i))
    #     if(distance < 5):
    #         print("10pi")
    #     if(distance < 7):
    #         print("14pi")
    #     else:
    #         print("Exceeds 14 pi")

            
    # ax = plt.figure().add_subplot(projection = '3d')
    



    # plt.axis((-5,5, -5,5,  -4,10))

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    theta = np.linspace(0, 2*np.pi, 360)
    y1 = 2*np.cos(theta)
    z1 = 2*np.sin(theta)


    ax.plot(y1,z1)
    ax.plot(x,y,z, 'o')

    plt.show()



if __name__ == "__main__":
    main()
