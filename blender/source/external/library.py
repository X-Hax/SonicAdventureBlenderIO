import ctypes
import os
import sys
from contextlib import contextmanager
from ..utility import general
from ..exceptions import SAIODevException, SAIOUserException

if general.is_x64():
    if general.is_arm():
        ARCHITECTURE_FOLDER = "arm64"
    else:
        ARCHITECTURE_FOLDER = "x64"
else:
    if general.is_arm():
        ARCHITECTURE_FOLDER = "arm"
    else:
        ARCHITECTURE_FOLDER = "x86"

if sys.platform == "win32":
    OS_FOLDER = "windows"
    LIB_EXT = ".dll"
elif sys.platform == "darwin":
    OS_FOLDER = "macos"
    LIB_EXT = ".dylib"
else:
    OS_FOLDER = "linux"
    LIB_EXT = ".so"

LIB_DIRECTORY = os.path.join(general.ADDON_DIR, "DLL", ARCHITECTURE_FOLDER, OS_FOLDER)

class ExternalLibrary:

    _LIBRARY: ctypes.CDLL | None = None

    @classmethod
    def _get_library_filename(cls):
        raise SAIODevException("Not Implemented")

    @classmethod
    def _get_library_function_args(cls) -> dict[str, tuple[tuple, any]]:
        raise SAIODevException("Not Implemented")

    @classmethod
    def _lib(cls):
        if cls._LIBRARY is None:
            raise SAIODevException("Library is not loaded")
        return cls._LIBRARY
    
    @classmethod
    @contextmanager
    def load(cls):
    
        if cls._LIBRARY is None:
            if len(LIB_EXT) == 0:
                raise SAIOUserException("Unknown/Unsupported Operating system!")

            if not os.path.isdir(LIB_DIRECTORY):
                raise SAIOUserException(f"External libraries are not compiled for {ARCHITECTURE_FOLDER} {OS_FOLDER}! Please open a github issue!")
            
            library_filepath = os.path.join(LIB_DIRECTORY, cls._get_library_filename() + LIB_EXT)
            cls._LIBRARY = ctypes.CDLL(library_filepath)
            cls._setup()

        try:
            yield cls
        finally:
            cls._cleanup()

            # I initially wanted to unload the library here,
            # but unfortunately that is not supported for
            # dotnet aot libraries:
            # https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/libraries

            # As such, it's not worth to unload any libraries here
                

    @classmethod
    def _setup(cls):
        lib = cls._lib()
        function_args = cls._get_library_function_args()

        for name, parameters in function_args.items():
            function = getattr(lib, name)
            function.argtypes = parameters[0]
            function.restype = parameters[1]
            
            if len(parameters) < 3:
                function.errcheck = cls._check_error

    @classmethod
    def _check_error(cls, result, func, arguments):
        return result

    @classmethod
    def _cleanup(cls):
        pass            

    
