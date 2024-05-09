import numpy as np
import numpy.typing as npt

def intersect_plane(plane_normal:npt.ArrayLike, plane_origin:npt.ArrayLike, ray_origin:npt.ArrayLike, ray_direction:npt.ArrayLike, t:float) -> bool:
    denominator:float = np.dot(plane_normal, ray_direction)
    if(denominator > 1e-6):
        p0l0:npt.ArrayLike = np.subtract(plane_origin, ray_origin)
        t = np.dot(p0l0, plane_normal) / denominator
        return (t >= 0)
    return False