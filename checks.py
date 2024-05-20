import numpy as np
import numpy.typing as npt

def normalize(vector:npt.ArrayLike) -> npt.ArrayLike:
    return vector / np.sqrt(np.dot(vector, vector))


def intersect_plane(plane_point:npt.ArrayLike, plane_normal:npt.ArrayLike, ray_origin:npt.ArrayLike, ray_direction:npt.ArrayLike):
    ray_direction = np.round(normalize(ray_direction - ray_origin), 4)
    print(ray_direction)
    if(ray_direction.dot(plane_normal) > 1e-6):
        t = np.round(((plane_point - ray_origin).dot(plane_normal)) / (ray_direction.dot(plane_normal)), 4)
        print(np.round(ray_origin + (ray_direction * t),4))
        print(t)


print(intersect_plane(
    plane_normal=np.array([0,0,1]),
    plane_point=np.array([0,0,0]),
    ray_origin=np.array([1,1,-2]),
    ray_direction=np.array([0,0,1]),
))