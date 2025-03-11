# Author: Isaac J. Boots

import numpy as np
import numpy.typing as npt

import stl


def normalize(vector: npt.NDArray) -> npt.NDArray:
    if np.dot(vector, vector) > 0:
        return vector / np.sqrt(np.dot(vector, vector))
    return vector


def distance_from_origin(point: npt.NDArray) -> float:
    return np.sqrt(np.sum(np.pow(point ,2)))


def intersect_triangle(
    ray_origin: npt.NDArray,
    ray_direction: npt.NDArray,
    v0: npt.NDArray,
    v1: npt.NDArray,
    v2: npt.NDArray,
) -> bool:
    v0v1: npt.NDArray = v1 - v0
    v0v2: npt.NDArray = v2 - v0
    # Normal of the triangle
    N: npt.NDArray = normalize(np.cross(v0v1, v0v2))

    # Calculate D, the distance from the origin to the plane
    D: float = -(np.dot(N, v0))

    if np.dot(N, ray_direction) < 1e-6:
        return False

    # Calculate t, scalar value representing the distance from the ray origin to the hit point
    t: float = -(np.dot(N, ray_origin) + D) / np.dot(N, ray_direction)

    # Calculate the hit postion
    p_hit: npt.NDArray = ray_origin + t * ray_direction

    # Determine if the point is inside of the triangle
    edge0: npt.NDArray = v1 - v0
    c: npt.ArrayLike = np.cross(edge0, p_hit - v0)
    if np.dot(N, c) < 0:
        return False

    edge1: npt.NDArray = v2 - v1
    c = np.cross(edge1, p_hit - v1)
    if np.dot(N, c) < 0:
        return False

    edge2: npt.NDArray = v0 - v2
    c = np.cross(edge2, p_hit - v2)
    if np.dot(N, c) < 0:
        return False

    return True


def is_centered(stl_object: stl.STLObject) -> bool:
    x_ray_origin: npt.NDArray = np.array([20, 0, 2])
    x_ray_direction: npt.NDArray = normalize(x_ray_origin - np.array([0, 0, 0]))

    y_ray_origin: npt.NDArray = np.array([0, 20, 2])
    y_ray_direction: npt.NDArray = normalize(y_ray_origin - np.array([0, 0, 0]))

    z_ray_origin: npt.NDArray = np.array([0, 0, 20])
    z_ray_direction: npt.NDArray = normalize(z_ray_origin - np.array([0, 0, 0]))

    x_intersection: bool = False
    y_intersection: bool = False
    z_intersection: bool = False

    for facet in stl_object.facets:
        if not x_intersection:
            x_intersection = intersect_triangle(
                x_ray_origin, x_ray_direction, facet.v1, facet.v2, facet.v3
            )
        if not y_intersection:
            y_intersection = intersect_triangle(
                y_ray_origin, y_ray_direction, facet.v1, facet.v2, facet.v3
            )
        if not z_intersection:
            z_intersection = intersect_triangle(
                z_ray_origin, z_ray_direction, facet.v1, facet.v2, facet.v3
            )
        else:
            return False

    return x_intersection and y_intersection and not z_intersection


def in_circle(stl_file: stl.STLObject, radius: int) -> bool:
    for facet in stl_file.facets:
        p1: npt.NDArray = facet.v1[0:2]
        p2: npt.NDArray = facet.v2[0:2]
        p3: npt.NDArray = facet.v3[0:2]
        if distance_from_origin(p1) >= radius:
            return False
        if distance_from_origin(p2) >= radius:
            return False
        if distance_from_origin(p3) >= radius:
            return False
    return True
