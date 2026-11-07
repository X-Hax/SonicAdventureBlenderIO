from ctypes import POINTER, pointer, byref, cast, sizeof, c_wchar, c_wchar_p, c_bool, c_int, c_uint
from typing import Iterable

from . import util
from .structs import *
from .nettypes import *
from .typing import TPointer

from .library import ExternalLibrary
from .functions.saio_net import FUNCTIONS

from ..exceptions import SAIOException

class SAIOLibraryException(SAIOException):
    function_name: str

    def __init__(self, message: str, function_name: str, *args: object):
        super().__init__(f"Library Exception when calling \"{function_name}\": {message}", *args)
        self.function_name = function_name

class SAIONET(ExternalLibrary):
    
    @classmethod
    def _get_library_filename(cls):
        return "SAIO.NET"
    
    @classmethod
    def _get_library_function_args(cls):
        return FUNCTIONS
    
    @classmethod
    def _setup(cls):
        super()._setup()

        size = c_int(sizeof(c_wchar))
        cls._lib().set_wchar_size(size)

    @classmethod
    def _check_error(cls, result, func, arguments):
        error = cls._LIBRARY.error_get()
        if error:
            raise SAIOLibraryException(error, func.__name__)
        
        return super()._check_error(result, func, arguments)
    
    @classmethod
    def _cleanup(cls):
        cls._LIBRARY.free_all()

    ################################################################################################
    # Matrix

    @classmethod
    def matrix_multiply(cls, a: CMatrix, b: CMatrix):
        return cls._lib().matrix_multiply(a, b)

    @classmethod
    def matrix_invert(cls, matrix: CMatrix):
        return cls._lib().matrix_invert(byref(matrix))

    @classmethod
    def matrix_create_translation(cls, position: CVector3) -> CMatrix:
        return cls._lib().matrix_create_translation(position)

    @classmethod
    def matrix_create_rotation(cls, euler_rotation: CVector3) -> CMatrix:
        return cls._lib().matrix_create_rotation(euler_rotation)

    @classmethod
    def matrix_create_from_quaternion(cls, quaternion: CQuaternion) -> CMatrix:
        return cls._lib().matrix_create_from_quaternion(quaternion)
    
    @classmethod
    def matrix_create_scale(cls, scale: CVector3) -> CMatrix:
        return cls._lib().matrix_create_scale(scale)

    @classmethod
    def matrix_decompose(cls, matrix: CMatrix):
        position = CVector3(0, 0, 0)
        rotation = CQuaternion(0, 0, 0, 1)
        scale = CVector3(1, 1, 1)

        cls._lib().matrix_decompose(matrix, byref(position), byref(rotation), byref(scale))

        return position, rotation, scale

    @classmethod
    def matrix_to_euler(cls, matrix: CMatrix):
        return cls._lib().matrix_to_euler(matrix)


    ################################################################################################
    # Quaternion

    @classmethod
    def quaternion_create_from_rotation_matrix(cls, matrix: CMatrix):
        return cls._lib().quaternion_create_from_rotation_matrix(matrix)

    ################################################################################################
    # Texture name

    @classmethod
    def texturename_read_file(cls, filepath: str):
        array = cls._lib().texturename_read_file(c_wchar_p(filepath))
        return util.array_to_list(array, c_wchar_p)

    @classmethod
    def texturename_write_file(cls, filepath: str, texture_names: list[str]):
        c_filepath = c_wchar_p(filepath)
        c_texture_names = util.as_array([c_wchar_p(texture_name) for texture_name in texture_names], c_wchar_p)
        c_texture_names_size = c_int(len(texture_names))
        
        cls._lib().texturename_write_file(c_filepath, c_texture_names, c_texture_names_size)
    
    ################################################################################################
    # Material

    @classmethod
    def material_get_hash(cls, material: TPointer[CMaterial]) -> int:
        return cls._lib().material_get_hash(material)

    ################################################################################################
    # Model

    @classmethod
    def model_read_files(cls, filepaths: list[str]) -> list[TPointer[CModel]]:
        c_filepaths = util.as_array([c_wchar_p(filepath) for filepath in filepaths], c_wchar_p)
        c_filepaths_size = c_int(len(filepaths))

        array = cls._lib().model_read_files(
            c_filepaths,
            c_filepaths_size
        )

        return util.array_to_list(array, POINTER(CModel))
    