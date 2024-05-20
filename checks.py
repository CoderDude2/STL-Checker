import numpy as np
import numpy.typing as npt

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
    N = np.cross(v0v1, v0v2)
    print(N)

intersect_triangle(
    ray_origin=np.array([1,0.5,0.5]),
    ray_direction=np.array([-1,0.5,0.5]),
    v0=np.array([0,0,0]),
    v1=np.array([0,0.5,1]),
    v2=np.array([0,1,0])
)

# print(intersect_plane(
#     plane_normal=np.array([0,0,1]),
#     plane_point=np.array([0,0,0]),
#     ray_origin=np.array([1,1,-2]),
#     ray_direction=np.array([0,0,1]),
# ))