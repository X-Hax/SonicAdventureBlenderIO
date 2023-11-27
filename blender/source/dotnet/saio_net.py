class SAIO_NET:
    '''SAIO.NET library types'''

    FLAGS: any = None
    '''class SAIO.NET.Flags'''

    CUTSCENE: any = None
    '''class SAIO.NET.Cutscene'''

    LAND_ENTRY_STRUCT: any = None
    '''struct SAIO.NET.LandEntryStruct'''

    LANDTABLE_WRAPPER: any = None
    '''class SAIO.NET.LandTableWrapper'''

    MESH_STRUCT: any = None
    '''struct SAIO.NET.MeshStruct'''

    MODEL: any = None
    '''class SAIO.NET.Model'''

    DEBUG_MODEL: any = None
    '''class SAIO.NET.DebugModel'''

    DEBUG_LEVEL: any = None
    '''class SAIO.NET.DebugLevel'''

    NODE_STRUCT: any = None
    '''struct SAIO.NET.NodeStruct'''

    CURVE_PATH: any = None
    '''class SAIO.NET.CurvePath'''

    PATH_DATA: any = None
    '''Class SAIO.NET.PathData'''

    TEXTURE: any = None
    '''class SAIO.NET.Texture'''

    @classmethod
    def load(cls):

        from SAIO.NET import (  # pylint: disable=import-error
            Flags,
            Cutscene,
            LandEntryStruct,
            LandTableWrapper,
            MeshStruct,
            Model,
            DebugModel,
            DebugLevel,
            NodeStruct,
            CurvePath,
            PathData,
            Texture
        )

        cls.FLAGS = Flags
        cls.CUTSCENE = Cutscene
        cls.LAND_ENTRY_STRUCT = LandEntryStruct
        cls.LANDTABLE_WRAPPER = LandTableWrapper
        cls.MESH_STRUCT = MeshStruct
        cls.MODEL = Model
        cls.DEBUG_MODEL = DebugModel
        cls.DEBUG_LEVEL = DebugLevel
        cls.NODE_STRUCT = NodeStruct
        cls.CURVE_PATH = CurvePath
        cls.PATH_DATA = PathData
        cls.TEXTURE = Texture

    @classmethod
    def unload(cls):
        cls.FLAGS = None
        cls.CUTSCENE = None
        cls.LAND_ENTRY_STRUCT = None
        cls.LANDTABLE_WRAPPER = None
        cls.MESH_STRUCT = None
        cls.MODEL = None
        cls.DEBUG_MODEL = None
        cls.DEBUG_LEVEL = None
        cls.NODE_STRUCT = None
        cls.CURVE_PATH = None
        cls.PATH_DATA = None
        cls.TEXTURE = None
