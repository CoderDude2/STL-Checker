# Author: Isaac J. Boots

import io
import struct
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import numpy.typing as npt

@dataclass
class Facet:
    normal: npt.NDArray[np.float64]
    v1: npt.NDArray[np.float64]
    v2: npt.NDArray[np.float64]
    v3: npt.NDArray[np.float64]


@dataclass
class STLObject:
    header: bytes
    facet_count: int
    facets: list[Facet]
    points: npt.NDArray[np.float64]
    name: str

    def length(self) -> float:
        min_z: float = self.facets[0].v1[2]
        max_z: float = self.facets[0].v1[2]
        for facet in self.facets:
            z1: float = facet.v1[2]
            z2: float = facet.v2[2]
            z3: float = facet.v3[2]

            if z1 > max_z:
                max_z = z1
            if z2 > max_z:
                max_z = z2
            if z3 > max_z:
                max_z = z3

            if z1 < min_z:
                min_z = z1
            if z2 < min_z:
                min_z = z2
            if z3 < min_z:
                min_z = z3
        return max_z - min_z

    def find_coordinate_system_by_edge_length(self, target_length: float, tolerance:float =1e-4):
        for facet in self.facets:
            edges = [
                (facet.v1, facet.v2),
                (facet.v2, facet.v3),
                (facet.v3, facet.v1)
            ]

            for p1, p2 in edges:
                vec = p2 - p1
                length = np.linalg.norm(vec)

                if np.isclose(length, target_length, atol=tolerance):
                    geometric_center = self.points.mean(axis=0)
                    print(np.round(geometric_center, 4))
                    x_axis = vec / length

                    normal_norm = np.linalg.norm(facet.normal)
                    if normal_norm == 0.0:
                        continue
                    print(f"{np.round(facet.normal, 4)}")
                    n_vec = facet.normal / normal_norm

                    y_axis = np.cross(n_vec, x_axis)
                    y_axis_len = np.linalg.norm(y_axis)
                    if np.isclose(y_axis_len, 0.0, atol=1e-7):
                        continue
                    y_axis /= y_axis_len
                    print(np.dot(n_vec, y_axis))

                    z_axis = np.cross(x_axis, y_axis)
                    midpoint = (p1 + p2) / 2.0

                    return np.round(x_axis, 4), np.round(y_axis, 4), np.round(z_axis, 4), np.round(midpoint, 4)


def read_facet(file_stream: io.BufferedReader) -> Facet:
    normal_bytes: bytes = file_stream.read(12)
    vertex1_bytes: bytes = file_stream.read(12)
    vertex2_bytes: bytes = file_stream.read(12)
    vertex3_bytes: bytes = file_stream.read(12)
    attribute_bytes: bytes = file_stream.read(2)

    ni: float = struct.unpack("f", normal_bytes[0:4])[0]
    nj: float = struct.unpack("f", normal_bytes[4:8])[0]
    nk: float = struct.unpack("f", normal_bytes[8:12])[0]

    v1_x: float = struct.unpack("f", vertex1_bytes[0:4])[0]
    v1_y: float = struct.unpack("f", vertex1_bytes[4:8])[0]
    v1_z: float = struct.unpack("f", vertex1_bytes[8:12])[0]

    v2_x: float = struct.unpack("f", vertex2_bytes[0:4])[0]
    v2_y: float = struct.unpack("f", vertex2_bytes[4:8])[0]
    v2_z: float = struct.unpack("f", vertex2_bytes[8:12])[0]

    v3_x: float = struct.unpack("f", vertex3_bytes[0:4])[0]
    v3_y: float = struct.unpack("f", vertex3_bytes[4:8])[0]
    v3_z: float = struct.unpack("f", vertex3_bytes[8:12])[0]

    f: Facet = Facet(
        normal=np.array([ni, nj, nk]),
        v1=np.array([v1_x, v1_y, v1_z]),
        v2=np.array([v2_x, v2_y, v2_z]),
        v3=np.array([v3_x, v3_y, v3_z]),
    )

    return f

def open_stl_file(file_path: str|Path) -> STLObject:
    if type(file_path) is Path:
        file_path = str(file_path)

    with open(file_path, "rb") as stl_file:
        header: bytes = stl_file.read(80)
        facet_count: int = int.from_bytes(stl_file.read(4), "little")
        facets: list[Facet] = []
        points = []
        vertexMap = {}
        vertex_id = 0

        for _ in range(facet_count):
            f: Facet = read_facet(stl_file)
            if tuple(f.v1) not in vertexMap:
                vertexMap[tuple(f.v1)] = vertex_id
                vertex_id += 1
            if tuple(f.v2) not in vertexMap:
                vertexMap[tuple(f.v2)] = vertex_id
                vertex_id += 1
            if tuple(f.v3) not in vertexMap:
                vertexMap[tuple(f.v3)] = vertex_id
                vertex_id += 1
            facets.append(f)
        
        temp = [np.array(i) for i in vertexMap.keys()]
        points = np.array(temp)
        #print(len(points))
        #print(points)
        
    stl: STLObject = STLObject(header=header, facet_count=facet_count, facets=facets, points=points, name=Path(file_path).name)
    return stl


def save_stl_file(file_path: str|Path, stl_object:STLObject, rotationMatrix: npt.NDArray|None = None):
    with open(file_path, "wb+") as stl_file:
        stl_file.write(bytes(stl_object.header))
        stl_file.write(struct.pack("<I", stl_object.facet_count))

        for facet in stl_object.facets:
            if not rotationMatrix is None:
                facet.normal = rotationMatrix @ facet.normal
                facet.v1 = rotationMatrix @ facet.v1
                facet.v2 = rotationMatrix @ facet.v2
                facet.v3 = rotationMatrix @ facet.v3
            facet_data = np.concatenate([facet.normal, facet.v1, facet.v2, facet.v3]).astype(np.float32)
            stl_file.write(facet_data.tobytes())
            stl_file.write(np.uint16(0).tobytes())


def main():
    stl_path = Path(r"C:\Users\TruUser\Documents\Development\STL-Checker\files\PDO-PL-0846604__(BH35-CS-TA10,6604).stl")
    stl_file = open_stl_file(stl_path)
    print(stl_file.facet_count)
    save_stl_file((stl_path.parent / "new" / stl_path.name), stl_file, None)


if __name__ == "__main__":
    main()