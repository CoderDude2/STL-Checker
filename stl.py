import math
import struct
import numpy as np
from dataclasses import dataclass
import io

class Vector3:
    def __init__(self, x:float = None, y:float = None, z:float = None) -> None:
        self.x = x if x is not None else 0
        self.y = y if y is not None else 0
        self.z = z if z is not None else 0

@dataclass
class Facet:
    normal:np.array
    v1:np.array
    v2:np.array
    v3:np.array

def dot(v1:Vector3, v2:Vector3) -> float:
    return (v1.x * v2.x) + (v1.y * v2.y) + (v1.z * v2.z)

def magnitude(v:Vector3) -> float:
    try:
        return math.sqrt(dot(v,v))
    except ZeroDivisionError:
        return 0

def normalize(v:Vector3) -> Vector3:
    new_vec = Vector3()
    vector_magnitude = magnitude(v)
    if(vector_magnitude > 0):
        inverse_length = 1 / vector_magnitude
        new_vec.x =  v.x * inverse_length
        new_vec.y = v.y * inverse_length
        new_vec.z = v.z * inverse_length
    return new_vec

def read_facet(file_stream:io.BufferedReader) -> Facet:
    normal_bytes = file_stream.read(12)
    vertex1_bytes = file_stream.read(12)
    vertex2_bytes = file_stream.read(12)
    vertex3_bytes = file_stream.read(12)
    attribute_bytes = file_stream.read(2)

    ni = struct.unpack('f', normal_bytes[0:4])[0]
    nj = struct.unpack('f', normal_bytes[4:8])[0]
    nk = struct.unpack('f', normal_bytes[8:12])[0]

    v1_x = struct.unpack('f', vertex1_bytes[0:4])[0]
    v1_y = struct.unpack('f', vertex1_bytes[4:8])[0]
    v1_z = struct.unpack('f', vertex1_bytes[8:12])[0]

    v2_x = struct.unpack('f', vertex2_bytes[0:4])[0]
    v2_y = struct.unpack('f', vertex2_bytes[4:8])[0]
    v2_z = struct.unpack('f', vertex2_bytes[8:12])[0]

    v3_x = struct.unpack('f', vertex3_bytes[0:4])[0]
    v3_y = struct.unpack('f', vertex3_bytes[4:8])[0]
    v3_z = struct.unpack('f', vertex3_bytes[8:12])[0]

    f = Facet(
        normal=np.array([ni, nj, nk]),
        v1=np.array([v1_x, v1_y, v1_z]),
        v2=np.array([v2_x, v2_y, v2_z]),
        v3=np.array([v3_x, v3_y, v3_z]),
    )

    return f

def open_stl_file(file_path:str) -> dict:
    stl_file = open(file_path, 'rb')
    header = stl_file.read(80)
    facet_count = int.from_bytes(stl_file.read(4), "little")

    facets = [read_facet(stl_file) for i in range(0, facet_count)]
    
    stl = {
        "header":header,
        "facet-count":facet_count,
        "facets":facets
    }

    return stl