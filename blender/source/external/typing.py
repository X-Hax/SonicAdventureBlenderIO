import ctypes
import typing

T = typing.TypeVar('T')

if typing.TYPE_CHECKING:

    class TPointer(typing.Generic[T], ctypes._Pointer):
        class _GenericAlias(typing.GenericAlias):
            def __repr__(self):
                val = super().__repr__()
                ibra = val.find('[')
                idot = val.rfind('.', 0, ibra)
                return f"{val[:idot+1]}POINTER{val[ibra:]}"

        def __class_getitem__(cls, *args):
            ptrtype = ctypes.POINTER(*args)
            alias = TPointer._GenericAlias(ptrtype, *args)
            return alias
else:
    class TPointer(typing.Generic[T]):
        pass