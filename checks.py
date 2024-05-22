import numpy as np
import numpy.typing as npt
import stl

def normalize(vector:npt.ArrayLike) -> npt.ArrayLike:
    return vector / np.sqrt(np.dot(vector, vector))


def intersect_plane(plane_point:npt.ArrayLike, 
                    plane_normal:npt.ArrayLike, 
                    ray_origin:npt.ArrayLike, 
                    ray_direction:npt.ArrayLike) -> bool:
    if(ray_direction.dot(plane_normal) > 1e-6):
        t = np.round(((plane_point - ray_origin).dot(plane_normal)) / (ray_direction.dot(plane_normal)), 4)
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
    print(N)

    # Calculate D, the distance from the origin to the plane
    D = -(np.dot(N, v0))

    if(np.dot(N, ray_direction) < 1e-6):
        return False

    # Calculate t, scalar value representing the distance from the ray origin to the hit point
    t = -(np.dot(N, ray_origin) + D) / np.dot(N, ray_direction)
    if(t < 0):
        return False

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


def is_centered(stl_object:stl.STLObject):
    for facet in stl_object.facets:
        x_ray_origin = np.array([20,0,0])
        x_ray_direction = x_ray_origin - np.array([0,0,0])

        intersect_triangle(
            x_ray_origin,
            x_ray_direction,
            facet.v1,
            facet.v2,
            facet.v3
        )


        print(facet.normal)
        print()

is_centered(stl.open_stl_file("stls/PDO-PL-0377326__(OTM-CS-TA14,7326).stl"))