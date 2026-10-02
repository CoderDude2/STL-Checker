from pathlib import Path
from dataclasses import dataclass

import csv
import numpy as np
import numpy.typing as npt

import stl
import abutment


@dataclass
class Vector3:
    x: float
    y: float
    z: float

@dataclass(frozen=True)
class Point3D:
    x: float
    y: float
    z: float

    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"

    def __eq__(self, other) -> bool:
        if self.x == other.x and self.y == other.y and self.z == other.z:
            return True
        return False

    def __sub__(self, other) -> Vector3:
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

@dataclass(frozen=True)
class Edge:
    p1: Point3D
    p2: Point3D

    def __eq__(self, other) -> bool:
        if (self.p1 == other.p1 and self.p2 == other.p2) or (self.p1 == other.p2 and self.p2 == other.p1):
            return True 
        return False

    def __hash__(self):
        return hash(frozenset((self.p1, self.p2)))
        
@dataclass
class Circle:
    center_point: Point3D
    radius: np.float64

    def __str__(self):
        return f"({self.center_point.x}, {self.center_point.y}) r={self.radius} z={self.center_point.z}"

def get_circle(p1: npt.NDArray, p2: npt.NDArray, p3: npt.NDArray) -> tuple|None:
    D: np.float64 = 2 * ((p1[0] * (p2[1] - p3[1])) + (p2[0] * (p3[1] - p1[1])) + (p3[0] * (p1[1] - p2[1])))

    if D == 0.0:
        return None

    xc_numerator: np.float64 = (p1[0]**2 + p1[1]**2) * (p2[1] - p3[1]) + (p2[0]**2 + p2[1]**2) * (p3[1] - p1[1]) + (p3[0]**2 + p3[1]**2) * (p1[1] - p2[1])
    yc_numerator: np.float64 = (p1[0]**2 + p1[1]**2) * (p3[0] - p2[0]) + (p2[0]**2 + p2[1]**2) * (p1[0] - p3[0]) + (p3[0]**2 + p3[1]**2) * (p2[0] - p1[0])

    center_point_x: np.float64 = xc_numerator / D
    center_point_y: np.float64 = yc_numerator / D

    center_point: npt.NDArray = np.array([center_point_x, center_point_y, p1[2]])
    
    r: np.float64 = np.sqrt(np.pow(p1[0] - center_point[0],2) + np.pow(p1[1] - center_point[1], 2))

    return tuple([center_point, r])

def get_circle3(points, target="outer"):
    pts = np.asarray(points)
    z_level = np.mean(pts[:, 2])
    
    x = pts[:, 0]
    y = pts[:, 1]
    
    # 1. Find a rough initial center using the median (robust against outliers)
    rough_cx = np.median(x)
    rough_cy = np.median(y)
    
    # 2. Calculate the radial distance of every point from this rough center
    radii = np.sqrt((x - rough_cx)**2 + (y - rough_cy)**2)
    
    # 3. Simple K-Means (K=2) thresholding to separate inner vs outer radii
    # We find a split threshold that cleanly divides the two rings
    min_r, max_r = np.min(radii), np.max(radii)
    threshold = (min_r + max_r) / 2.0
    
    # Iterate a few times to stabilize the threshold boundary
    for _ in range(5):
        inner_group = radii[radii <= threshold]
        outer_group = radii[radii > threshold]
        if len(inner_group) == 0 or len(outer_group) == 0:
            break
        threshold = (np.mean(inner_group) + np.mean(outer_group)) / 2.0
    
    # 4. Filter the points based on your target selection
    if target == "outer":
        mask = radii > threshold
    else:
        mask = radii <= threshold
        
    clean_x = x[mask]
    clean_y = y[mask]
    
    # Fail-safe: if clustering failed to split meaningful groups, fall back to all points
    if len(clean_x) < 3:
        clean_x, clean_y = x, y

    # 5. Run the Algebraic Least Squares Fit on the clean point set
    A = np.column_stack((clean_x, clean_y, np.ones_like(clean_x)))
    B = clean_x**2 + clean_y**2
    
    a, b, c = np.linalg.lstsq(A, B, rcond=None)[0]
    
    center_x = a / 2.0
    center_y = b / 2.0
    final_radius = np.sqrt(c + center_x**2 + center_y**2)
    
    return np.array([center_x, center_y, z_level]), final_radius

def get_circle2(points) -> tuple|None:
    pts = np.asarray(points)

    z_level = np.mean(pts[:, 2])

    x = pts[:, 0]
    y = pts[:, 1]

    A = np.column_stack((x, y, np.ones_like(x)))
    B = x**2 + y**2

    a, b, c = np.linalg.lstsq(A, B, rcond=None)[0]

    center_x = a / 2.0
    center_y = b / 2.0
    radius = np.sqrt(c + center_x**2 + center_y**2)

    center_3d = np.array([center_x, center_y, z_level])

    return tuple([center_3d, radius])

def get_circles(stl_file: stl.STLObject) -> list[tuple]:
    zMap = {}

    for point in stl_file.points:
        if not zMap.get(np.round(point, 4)[2]):
            zMap[np.round(point, 4)[2]] = [point]
        else:
            zMap[np.round(point, 4)[2]].append(point)

    circles = {}

    for key, val in zMap.items():
        if len(val) > 20:
            circles[key] = val

    result: list[tuple] = []
    for val in circles.values():
        cir = get_circle3(val, "outer")
        if cir is not None:
            result.append(cir)

    return sorted(result, key=lambda i: i[0][2]) 

def orient_and_center_stl(stl_file: stl.STLObject, edge_length):
    res = (stl_file.find_coordinate_system_by_edge_length(edge_length))
    print(res)

    if res is None:
        print("exiting orient and center")
        return None

    geometric_center = stl_file.points.mean(axis=0)

    Lx, Ly, Lz, c = res

    to_center = geometric_center - c
    to_center /= np.linalg.norm(to_center)

    dot_y = np.dot(Ly, to_center)
    dot_z = np.dot(Lz, to_center)

    if np.abs(dot_y) > np.abs(dot_z):
        true_z = Ly if dot_y > 0 else -Ly
    else:
        true_z = Lz if dot_z > 0 else -Lz

    true_y = np.cross(true_z, Lx)
    true_y /= np.linalg.norm(true_y)

    M_local = np.column_stack((Lx, true_y, true_z))

    targetX = np.array([1,0,0])
    targetY = np.array([0,1,0])
    targetZ = np.array([0,0,1])
    M_target = np.column_stack((targetX, targetY, targetZ))
    R = M_target @ M_local.T

    for facet in stl_file.facets:
        facet.normal = facet.normal @ R.T 
        facet.v1 = facet.v1 @ R.T
        facet.v2 = facet.v2 @ R.T
        facet.v3 = facet.v3 @ R.T

    stl_file.points = stl_file.points @ R.T

    circles = get_circles(stl_file)
    print(f"# of circles: {len(circles)}")
    if len(circles) > 5:
        lowest_z_cir = circles[3]
        shift = np.array([0,0,0]) - lowest_z_cir[0]
        for facet in stl_file.facets:
            facet.v1 += shift
            facet.v2 += shift 
            facet.v3 += shift 


        edge_midpoint = (c @ R.T) + shift
        to_edge = np.array([edge_midpoint[0], edge_midpoint[1], 0]) 

        if np.dot(targetY, to_edge) < 0:
            R180 = np.array([
                [-1, 0, 0],
                [0, -1, 0],
                [0, 0, 1]
            ])

            for facet in stl_file.facets:
                facet.normal = facet.normal @ R180 
                facet.v1 = facet.v1 @ R180
                facet.v2 = facet.v2 @ R180
                facet.v3 = facet.v3 @ R180

            stl_file.points = stl_file.points @ R180
    return stl_file

# file = Path(r"C:\Users\TruUser\Documents\Development\STL-Checker\files\PDO-PL-0846604__(BH35-CS-TA10,6604).stl")
# stl_file = stl.open_stl_file(file)
# edge_length = 0.9260
# edge_length = 0.6400

# for file in Path(r"C:\Users\TruUser\Documents\Development\STL-Checker\files").iterdir():
#     if file.is_dir():
#         continue
#     m = abutment.case_regex.match(file.name)
#     if m:
#         print(m["connection"])
#         stl_file = stl.open_stl_file(file)
#         orient_and_center_stl(stl_file, edge_length)

def main():
    csv_file = Path(r"C:\Users\TruUser\Desktop\vals.csv")
    files_folder = Path(r"C:\Users\TruUser\Documents\Development\STL-Checker\files")

    connections = {}
    with csv_file.open(newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if connections.get(row[0]) is None:
                connections[row[0]] = float(row[1])

    for file in files_folder.iterdir():
        m = abutment.case_regex.match(file.name)

        if not m:
            continue

        print(file.name, m["connection"])

        if not connections.get(m["connection"]):
            continue

        new_stl_file = orient_and_center_stl(stl.open_stl_file(file.absolute()), connections[m["connection"]])
        if new_stl_file is None:
            continue
        stl.save_stl_file(file.absolute(), new_stl_file)
        print()

if __name__ == "__main__":
    main()