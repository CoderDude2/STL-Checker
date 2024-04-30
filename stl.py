import math

class Vector3:
    def __init__(self, x:float = None, y:float = None, z:float = None) -> None:
        self.x = x if x is not None else 0
        self.y = y if y is not None else 0
        self.z = z if z is not None else 0

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

def open_stl_file(file_path) -> dict:
    raise NotImplementedError