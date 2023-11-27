class System:
    '''.NET System types'''

    VALUE_TUPLE: any = None
    '''struct System.ValueTuple'''

    INT16: any = None
    '''struct System.Int16'''

    UINT32: any = None
    '''struct System.UInt32'''

    VECTOR3: any = None
    '''struct System.Numerics.Vector3'''

    VECTOR2: any = None
    '''struct System.Numerics.Vector2'''

    MATRIX4X4: any = None
    '''struct System.Numerics.Matrix4x4'''

    ARRAY: any = None
    '''class System.Array'''

    DICTIONARY: any = None
    '''class System.Collections.Generic.Dictionary<TKey, TValue>'''

    SORTED_DICTIONARY: any = None
    '''class System.Collections.Generic.SortedDictionary<TKey, TValue>'''

    FILE: any = None
    '''class System.IO.File'''

    @classmethod
    def load(cls):

        from System import (  # pylint: disable=import-error
            ValueTuple,
            Int16,
            UInt32,
            Array
        )

        from System.Numerics import (  # pylint: disable=import-error
            Vector3,
            Vector2,
            Matrix4x4
        )

        from System.Collections.Generic import SortedDictionary  # pylint: disable=import-error
        from System.Collections.Generic import Dictionary  # pylint: disable=import-error

        from System.IO import File  # pylint: disable=import-error

        cls.VALUE_TUPLE = ValueTuple
        cls.INT16 = Int16
        cls.UINT32 = UInt32
        cls.VECTOR3 = Vector3
        cls.VECTOR2 = Vector2
        cls.MATRIX4X4 = Matrix4x4
        cls.ARRAY = Array
        cls.DICTIONARY = Dictionary
        cls.SORTED_DICTIONARY = SortedDictionary
        cls.FILE = File

    @classmethod
    def unload(cls):
        cls.VALUE_TUPLE = None
        cls.INT16 = None
        cls.UINT32 = None
        cls.VECTOR3 = None
        cls.VECTOR2 = None
        cls.MATRIX4X4 = None
        cls.ARRAY = None
        cls.DICTIONARY = None
        cls.SORTED_DICTIONARY = None
        cls.File = None
