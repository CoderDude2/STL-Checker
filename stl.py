# Author: Isaac J. Boots

import io
import struct
from dataclasses import dataclass

import numpy as np
import numpy.typing as npt


@dataclass
class Facet:
    normal:npt.ArrayLike
    v1:npt.ArrayLike
    v2:npt.ArrayLike
    v3:npt.ArrayLike

@dataclass
class STLObject:
    header:bytes
    facet_count:int
    facets:list[Facet]

    def in_circle_10pi(self) -> bool:
        for facet in self.facets:
            p1:npt.ArrayLike = np.array([facet.v1[0], facet.v1[1]])
            p2:npt.ArrayLike = np.array([facet.v2[0], facet.v2[1]])
            p3:npt.ArrayLike = np.array([facet.v3[0], facet.v3[1]])
            if(distance_from_origin(p1) >= 5):
                return False
            if(distance_from_origin(p2) >= 5):
                return False
            if(distance_from_origin(p3) >= 5):
                return False
        return True
    
    def in_circle_14pi(self) -> bool:
        for facet in self.facets:
            p1:npt.ArrayLike = np.array([facet.v1[0], facet.v1[1]])
            p2:npt.ArrayLike = np.array([facet.v2[0], facet.v2[1]])
            p3:npt.ArrayLike = np.array([facet.v3[0], facet.v3[1]])
            if(distance_from_origin(p1) >= 7):
                return False
            if(distance_from_origin(p2) >= 7):
                return False
            if(distance_from_origin(p3) >= 7):
                return False
        return True
    
    def length(self) -> float:
        min_z:float = self.facets[0].v1[2]
        max_z:float = self.facets[0].v1[2]

        for facet in self.facets:
            z1:float = facet.v1[2]
            z2:float = facet.v2[2]
            z3:float = facet.v3[2]

            max_z = z1 if z1 > max_z else max_z
            max_z = z2 if z3 > max_z else max_z
            max_z = z3 if z3 > max_z else max_z

            min_z = z1 if z1 < min_z else min_z
            min_z = z2 if z3 < min_z else min_z
            min_z = z3 if z3 < min_z else min_z
        return max_z - min_z

def read_facet(file_stream:io.BufferedReader) -> Facet:
    normal_bytes:bytes = file_stream.read(12)
    vertex1_bytes:bytes = file_stream.read(12)
    vertex2_bytes:bytes = file_stream.read(12)
    vertex3_bytes:bytes = file_stream.read(12)
    attribute_bytes:bytes = file_stream.read(2)

    ni:float = struct.unpack('f', normal_bytes[0:4])[0]
    nj:float = struct.unpack('f', normal_bytes[4:8])[0]
    nk:float = struct.unpack('f', normal_bytes[8:12])[0]

    v1_x:float = struct.unpack('f', vertex1_bytes[0:4])[0]
    v1_y:float = struct.unpack('f', vertex1_bytes[4:8])[0]
    v1_z:float = struct.unpack('f', vertex1_bytes[8:12])[0]

    v2_x:float = struct.unpack('f', vertex2_bytes[0:4])[0]
    v2_y:float = struct.unpack('f', vertex2_bytes[4:8])[0]
    v2_z:float = struct.unpack('f', vertex2_bytes[8:12])[0]

    v3_x:float = struct.unpack('f', vertex3_bytes[0:4])[0]
    v3_y:float = struct.unpack('f', vertex3_bytes[4:8])[0]
    v3_z:float = struct.unpack('f', vertex3_bytes[8:12])[0]

    f:Facet = Facet(
        normal=np.array([ni, nj, nk]),
        v1=np.array([v1_x, v1_y, v1_z]),
        v2=np.array([v2_x, v2_y, v2_z]),
        v3=np.array([v3_x, v3_y, v3_z]),
    )

    return f

def distance_from_origin(point:np.array) -> float:
    return np.sqrt(point[0]**2 + point[1]**2)

def open_stl_file(file_path:str) -> STLObject:
    stl_file:io.BufferedReader = open(file_path, 'rb')
    header:bytes = stl_file.read(80)
    facet_count:int = int.from_bytes(stl_file.read(4), "little")

    facets:list[Facet] = [read_facet(stl_file) for i in range(0, facet_count)]
    stl:STLObject = STLObject(header=header, facet_count=facet_count, facets=facets)

    return stl