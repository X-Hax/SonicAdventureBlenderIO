from ctypes import Structure, c_float, c_int

class CVector2(Structure):
    _fields_ = [
        ("x", c_float),
        ("y", c_float),
    ]
    
    x: float
    y: float

class CVector3(Structure):
    _fields_ = [
        ("x", c_float),
        ("y", c_float),
        ("z", c_float),
    ]
    
    x: float
    y: float
    z: float

class CVector4(Structure):
    _fields_ = [
        ("x", c_float),
        ("y", c_float),
        ("z", c_float),
        ("w", c_float),
    ]
    
    x: float
    y: float
    z: float
    w: float

class CQuaternion(Structure):
    _fields_ = [
        ("x", c_float),
        ("y", c_float),
        ("z", c_float),
        ("w", c_float),
    ]
    
    x: float
    y: float
    z: float
    w: float

class CMatrix(Structure):
    _fields_ = [
        ("m11", c_float),
        ("m12", c_float),
        ("m13", c_float),
        ("m14", c_float),
        ("m21", c_float),
        ("m22", c_float),
        ("m23", c_float),
        ("m24", c_float),
        ("m31", c_float),
        ("m32", c_float),
        ("m33", c_float),
        ("m34", c_float),
        ("m41", c_float),
        ("m42", c_float),
        ("m43", c_float),
        ("m44", c_float),
    ]
    
    m11: float
    m12: float
    m13: float
    m14: float
    m21: float
    m22: float
    m23: float
    m24: float
    m31: float
    m32: float
    m33: float
    m34: float
    m41: float
    m42: float
    m43: float
    m44: float


