import matplotlib.pyplot as plt

import numpy as np
import numpy.typing as npt
import stl

import time

def normalize(vector:npt.ArrayLike) -> npt.ArrayLike:
    if(np.dot(vector, vector) > 0):
        return vector / np.sqrt(np.dot(vector, vector))
    return vector

def intersect_plane(plane_point:npt.ArrayLike, 
                    plane_normal:npt.ArrayLike, 
                    ray_origin:npt.ArrayLike, 
                    ray_direction:npt.ArrayLike) -> bool:
    if(ray_direction.dot(plane_normal) > 1e-6):
        t:float = np.round(((plane_point - ray_origin).dot(plane_normal)) / (ray_direction.dot(plane_normal)), 4)
        return t >= 0
    return False

def intersect_triangle(ray_origin:npt.ArrayLike, 
                       ray_direction:npt.ArrayLike,
                       v0:npt.ArrayLike, 
                       v1:npt.ArrayLike, 
                       v2:npt.ArrayLike) -> bool:
    v0v1:npt.ArrayLike = v1 - v0
    v0v2:npt.ArrayLike = v2 - v0
    # Normal of the triangle
    N:npt.ArrayLike = normalize(np.cross(v0v1, v0v2))

    # Calculate D, the distance from the origin to the plane
    D:float = -(np.dot(N, v0))

    if(np.dot(N, ray_direction) < 1e-6):
        return False

    # Calculate t, scalar value representing the distance from the ray origin to the hit point
    t:float = -(np.dot(N, ray_origin) + D) / np.dot(N, ray_direction)
    # if(t > 0):
    #     return False

    # Calculate the hit postion
    p_hit:npt.ArrayLike = ray_origin + t * ray_direction

    edge0:npt.ArrayLike = v1 - v0
    c:npt.ArrayLike = np.cross(edge0, p_hit - v0)
    if(np.dot(N, c)  < 0):
        return False
    
    edge1:npt.ArrayLike = v2 - v1
    c:npt.ArrayLike = np.cross(edge1, p_hit - v1)
    if(np.dot(N, c)  < 0):
        return False
    

    edge2:npt.ArrayLike = v0 - v2
    c:npt.ArrayLike = np.cross(edge2, p_hit - v2)
    if(np.dot(N, c)  < 0):
        return False
    
    return True

def is_centered(stl_object:stl.STLObject) -> bool:
    x_ray_origin:npt.ArrayLike = np.array([20,0,2])
    x_ray_direction:npt.ArrayLike = normalize(x_ray_origin - np.array([0,0,0]))

    y_ray_origin:npt.ArrayLike = np.array([0,20,2])
    y_ray_direction:npt.ArrayLike = normalize(y_ray_origin - np.array([0,0,0]))

    z_ray_origin:npt.ArrayLike = np.array([0,0,20])
    z_ray_direction:npt.ArrayLike = normalize(z_ray_origin - np.array([0,0,0]))

    x_intersection:bool = False
    y_intersection:bool = False
    z_intersection:bool = False

    for facet in stl_object.facets:
        x_intersection = intersect_triangle(x_ray_origin, x_ray_direction, facet.v1, facet.v2, facet.v3) if x_intersection == False else x_intersection
        y_intersection = intersect_triangle(y_ray_origin, y_ray_direction, facet.v1, facet.v2, facet.v3) if y_intersection == False else y_intersection
        z_intersection = intersect_triangle(z_ray_origin, z_ray_direction, facet.v1, facet.v2, facet.v3) if z_intersection == False else z_intersection

    if(x_intersection and y_intersection and not z_intersection):
        return True
    
    return False

def is_centered_visualized(stl_object:stl.STLObject) -> None:
    x_ray_origin:npt.ArrayLike = np.array([20,0,2])
    x_ray_direction:npt.ArrayLike = normalize(x_ray_origin - np.array([0,0,0]))

    y_ray_origin:npt.ArrayLike = np.array([0,20,2])
    y_ray_direction:npt.ArrayLike = normalize(y_ray_origin - np.array([0,0,0]))

    z_ray_origin:npt.ArrayLike = np.array([0,0,20])
    z_ray_direction:npt.ArrayLike = normalize(z_ray_origin - np.array([0,0,0]))

    fig:plt.Figure = plt.figure()
    ax:plt.Axes = fig.add_subplot(111, projection='3d')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    x:list[float] = []
    y:list[float] = []
    z:list[float] = []

    int_x_0:list[float] = []
    int_y_0:list[float] = []
    int_z_0:list[float] = []

    int_x_1:list[float] = []
    int_y_1:list[float] = []
    int_z_1:list[float] = []

    int_x_2:list[float] = []
    int_y_2:list[float] = []
    int_z_2:list[float] = []

    ax.plot(0,0,0,'o', color="green")
    for facet in stl_object.facets:
        if(intersect_triangle(x_ray_origin, x_ray_direction, facet.v1, facet.v2, facet.v3)):
            int_x_0.append(facet.v1[0])
            int_x_0.append(facet.v2[0])
            int_x_0.append(facet.v3[0])

            int_y_0.append(facet.v1[1])
            int_y_0.append(facet.v2[1])
            int_y_0.append(facet.v3[1])

            int_z_0.append(facet.v1[2])
            int_z_0.append(facet.v2[2])
            int_z_0.append(facet.v3[2])
        elif(intersect_triangle(y_ray_origin, y_ray_direction, facet.v1, facet.v2, facet.v3)):
            int_x_1.append(facet.v1[0])
            int_x_1.append(facet.v2[0])
            int_x_1.append(facet.v3[0])

            int_y_1.append(facet.v1[1])
            int_y_1.append(facet.v2[1])
            int_y_1.append(facet.v3[1])

            int_z_1.append(facet.v1[2])
            int_z_1.append(facet.v2[2])
            int_z_1.append(facet.v3[2])
        elif(intersect_triangle(z_ray_origin, z_ray_direction, facet.v1, facet.v2, facet.v3)):
            int_x_2.append(facet.v1[0])
            int_x_2.append(facet.v2[0])
            int_x_2.append(facet.v3[0])

            int_y_2.append(facet.v1[1])
            int_y_2.append(facet.v2[1])
            int_y_2.append(facet.v3[1])

            int_z_2.append(facet.v1[2])
            int_z_2.append(facet.v2[2])
            int_z_2.append(facet.v3[2])
        else:
            x.append(facet.v1[0])
            x.append(facet.v2[0])
            x.append(facet.v3[0])

            y.append(facet.v1[1])
            y.append(facet.v2[1])
            y.append(facet.v3[1])

            z.append(facet.v1[2])
            z.append(facet.v2[2])
            z.append(facet.v3[2])
            
    ax.plot(x,y,z,'o',color="grey")
    ax.plot(int_x_0, int_y_0, int_z_0, 'o', color="red")
    ax.plot(int_x_1, int_y_1, int_z_1, 'o', color="green")
    ax.plot(int_x_2, int_y_2, int_z_2, 'o', color="blue")
    plt.show()