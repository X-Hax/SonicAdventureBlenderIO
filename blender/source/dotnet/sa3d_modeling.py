from .system import System

class SA3D_Modeling:
    '''SA3D.Modeling library types'''

    COLOR: any = None
    '''Struct SA3D.Modeling.'''

    ATTACHFORMAT: any = None
    '''Enum SA3D.Modeling.'''

    BLENDMODE: any = None
    '''Enum SA3D.Modeling.'''

    FILTERMODE: any = None
    '''Enum SA3D.Modeling.'''

    GC_TEXCOORD_ID: any = None
    '''Enum SA3D.Modeling.'''

    GC_TEXCOORD_MATRIX: any = None
    '''Enum SA3D.Modeling.'''

    GC_TEXCOORD_SOURCE: any = None
    '''Enum SA3D.Modeling.'''

    GC_TEXCOORD_TYPE: any = None
    '''Enum SA3D.Modeling.'''

    BUFFER_MATERIAL: any = None
    '''Struct SA3D.Modeling.'''

    BUFFER_CORNER: any = None
    '''Struct SA3D.Modeling.'''

    WEIGHTED_VERTEX: any = None
    '''Struct SA3D.Modeling.'''

    MODELFORMAT: any = None
    '''Enum SA3D.Modeling.'''

    MOTION: any = None
    '''Class SA3D.Modeling.Animation.Motion'''

    KEYFRAMES: any = None
    '''Class SA3D.Modeling.Animation.Keyframes'''

    KEYFRAME_ATTRIBUTES: any = None
    '''Enum SA3D.Modeling.Animation.KeyframeAttributes'''

    KEYFRAME_ROTATION_UTILS: any = None
    '''Class SA3D.Modeling.Animation.Utils.KeyframeRotationUtils'''

    MODEL_FILE: any = None
    '''Class SA3D.Modeling.File.ModelFile'''

    LEVEL_FILE: any = None
    '''Class SA3D.Modeling.File.LevelFile'''

    ANIMATION_FILE: any = None
    '''Class SA3D.Modeling.File.AnimationFile'''

    META_DATA: any = None
    '''Class SA3D.Modeling.File.MetaData'''

    GEN_MATRIX_KEYFRAMES: any = None
    '''Generic type: SortedDictionary<uint, Matrix4x4>'''

    GEN_COMPLEMENTARY_MATRIX_DICT: any = None
    '''Generic type: Dictionary<uint, Matrix4x4[]>'''

    @classmethod
    def load(cls):
        from SA3D.Modeling.Structs import Color  # pylint: disable=import-error

        from SA3D.Modeling.Mesh import (  # pylint: disable=import-error
            AttachFormat,
            BlendMode,
            FilterMode,
        )

        from SA3D.Modeling.Mesh.GC import (  # pylint: disable=import-error
            GCTexCoordID,
            GCTexcoordMatrix,
            GCTexCoordSource,
            GCTexCoordType,
        )

        from SA3D.Modeling.Mesh.Buffer import (  # pylint: disable=import-error
            BufferMaterial,
            BufferCorner,
        )

        from SA3D.Modeling.Mesh.Weighted import WeightedVertex  # pylint: disable=import-error

        from SA3D.Modeling.ObjectData.Enums import ModelFormat  # pylint: disable=import-error


        from SA3D.Modeling.Animation import (  # pylint: disable=import-error
            Motion,
            Keyframes,
            KeyframeAttributes,
        )

        from SA3D.Modeling.Animation.Utils import KeyframeRotationUtils  # pylint: disable=import-error

        from SA3D.Modeling.File import (  # pylint: disable=import-error
            ModelFile,
            LevelFile,
            AnimationFile,
            MetaData,
        )

        cls.COLOR = Color
        cls.ATTACHFORMAT = AttachFormat
        cls.BLENDMODE = BlendMode
        cls.FILTERMODE = FilterMode
        cls.GC_TEXCOORD_ID = GCTexCoordID
        cls.GC_TEXCOORD_MATRIX = GCTexcoordMatrix
        cls.GC_TEXCOORD_SOURCE = GCTexCoordSource
        cls.GC_TEXCOORD_TYPE = GCTexCoordType
        cls.BUFFER_MATERIAL = BufferMaterial
        cls.BUFFER_CORNER = BufferCorner
        cls.WEIGHTED_VERTEX = WeightedVertex
        cls.MODELFORMAT = ModelFormat
        cls.MOTION = Motion
        cls.KEYFRAMES = Keyframes
        cls.KEYFRAME_ATTRIBUTES = KeyframeAttributes
        cls.KEYFRAME_ROTATION_UTILS = KeyframeRotationUtils
        cls.MODEL_FILE = ModelFile
        cls.LEVEL_FILE = LevelFile
        cls.ANIMATION_FILE = AnimationFile
        cls.META_DATA = MetaData

        cls.GEN_MATRIX_KEYFRAMES = System.SORTED_DICTIONARY[System.UINT32, System.MATRIX4X4] # pylint: disable=unsubscriptable-object
        cls.GEN_COMPLEMENTARY_MATRIX_DICT = System.DICTIONARY[System.UINT32, System.ARRAY[System.MATRIX4X4]] # pylint: disable=unsubscriptable-object

    @classmethod
    def unload(cls):
        cls.COLOR = None
        cls.ATTACHFORMAT = None
        cls.MODELFORMAT = None
        cls.BLENDMODE = None
        cls.FILTERMODE = None
        cls.GC_TEXCOORD_ID = None
        cls.GC_TEXCOORD_MATRIX = None
        cls.GC_TEXCOORD_SOURCE = None
        cls.GC_TEXCOORD_TYPE = None
        cls.BUFFER_MATERIAL = None
        cls.BUFFER_CORNER = None
        cls.WEIGHTED_VERTEX = None
        cls.MOTION = None
        cls.KEYFRAMES = None
        cls.KEYFRAME_ATTRIBUTES = None
        cls.KEYFRAME_ROTATION_UTILS = None
        cls.MODEL_FILE = None
        cls.LEVEL_FILE = None
        cls.ANIMATION_FILE = None
        cls.META_DATA = None
        cls.GEN_MATRIX_KEYFRAMES = None
        cls.GEN_COMPLEMENTARY_MATRIX_DICT = None
