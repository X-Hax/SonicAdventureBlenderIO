import ctypes
from typing import Iterable
from .structs import CArray

def pointer_to_address(pointer):
    return ctypes.cast(pointer, ctypes.c_void_p).value

def as_array(iterable: Iterable, type):
    if iterable is None:
        return ctypes.POINTER(type)()

    array = (type * len(iterable))(*iterable)
    return ctypes.cast(array, ctypes.POINTER(type))

def construct_array(iterable: Iterable, type):
    if iterable is None:
        return ctypes.POINTER(type)()
    
    return as_array([type(x) for x in iterable], type)

def array_to_list(array: CArray, target_type):
    result = []

    item_pointer = ctypes.cast(array.array, ctypes.POINTER(target_type))
    for i in range(array.size):
        result.append(item_pointer[i])

    return result