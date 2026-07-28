# Author: Isaac J. Boots

import numpy as np
import numpy.typing as npt
import random
import sys
from dataclasses import dataclass
from pathlib import Path

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

@dataclass
class Point3D:
    x: np.float64
    y: np.float64
    z: np.float64

    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"

@dataclass
class Circle:
    center_point: Point3D
    radius: np.float64

    def __str__(self):
        return f"({self.center_point.x}, {self.center_point.y}) r={self.radius} z={self.center_point.z}"

def distance(p1:Point3D, p2:Point3D) -> np.float64:
    return np.sqrt(np.pow(p1.x - p2.x, 2) + np.pow(p1.y - p2.y, 2))

def midpoint(p1:Point3D, p2:Point3D) -> Point3D:
    return Point3D((p1.x + p2.x) / 2, (p1.y + p2.y) / 2, p1.z)

def get_circle(p1: Point3D, p2: Point3D, p3: Point3D) -> Circle|None:
    D: np.float64 = 2 * ((p1.x * (p2.y - p3.y)) + (p2.x * (p3.y - p1.y)) + (p3.x * (p1.y - p2.y)))

    if D == 0.0:
        return None

    xc_numerator: np.float64 = (p1.x**2 + p1.y**2) * (p2.y - p3.y) + (p2.x**2 + p2.y**2) * (p3.y - p1.y) + (p3.x**2 + p3.y**2) * (p1.y - p2.y)
    yc_numerator: np.float64 = (p1.x**2 + p1.y**2) * (p3.x - p2.x) + (p2.x**2 + p2.y**2) * (p1.x - p3.x) + (p3.x**2 + p3.y**2) * (p2.x - p1.x)

    center_point_x: np.float64 = np.round(xc_numerator / D, 6)
    center_point_y: np.float64 = np.round(yc_numerator / D, 6)

    center_point: Point3D = Point3D(center_point_x, center_point_y, p1.z)
    
    r: np.float64 = distance(p1, center_point)

    return Circle(center_point, r)



def get_all_circles(stl_file: stl.STLObject) -> list[Circle]:
    zMap = {}
    
    for point in stl_file.points:
        rounded_z_val = np.round(point[2], 4)
        if not zMap.get(rounded_z_val):
            zMap[rounded_z_val] = [Point3D(np.round(point[0], 6), np.round(point[1], 6), np.round(point[2], 6))]
        else:
            zMap[rounded_z_val].append(Point3D(np.round(point[0], 6), np.round(point[1], 6), np.round(point[2], 6)))
    
    circles = {}

    for key, val in zMap.items():
        if len(val) > 24 and len(val) < 30:
            circles[key] = val
    
    result: list[Circle] = []

    for val in circles.values():
        cir = get_circle(val[0], val[1], val[2])

        if cir is not None and round(cir.center_point.x, 2) == 0 and round(cir.center_point.x, 2) == 0:    
            if round(cir.radius, 2) >= 1.15 and round(cir.radius, 2) < 1.3:
                result.append(cir)
    
    return result

def is_asc_ds_mistmatch(stl_path: str|Path) -> bool:
    if type(stl_path) is str:
        stl_path = Path(stl_path)

    stl_file:stl.STLObject = stl.open_stl_file(stl_path)
    max_z_index_cir: Circle|None = None
    for cir in get_all_circles(stl_file):
        if max_z_index_cir is None:
            max_z_index_cir = cir
            continue
        
        if cir.center_point.z > max_z_index_cir.center_point.z:
            max_z_index_cir = cir
    if max_z_index_cir:
        if "TA" in stl_file.name and max_z_index_cir.radius > 1.17 and max_z_index_cir.radius < 1.3:
            return True
    return False

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