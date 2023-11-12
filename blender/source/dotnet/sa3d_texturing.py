class SA3D_Texturing:
    '''SA3D.Texturing library types'''

    TEXTURE_SET: any = None
    '''Class SA3D.Texturing.TextureSet'''

    TEXTURE_NAME_LIST: any = None
    '''Class SA3D.Texturing.Texname.TextureNameList'''

    TEXTURE_NAME: any = None
    '''Class SA3D.Texturing.Texname.TextureName'''

    INDEX_TEXTURE: any = None
    '''Class SA3D.Texturing.IndexTexture'''

    @classmethod
    def load(cls):

        from SA3D.Texturing.Texname import (  # pylint: disable=import-error
            TextureSet,
            TextureNameList,
            TextureName,
            IndexTexture
        )

        cls.TEXTURE_SET = TextureSet
        cls.TEXTURE_NAME_LIST = TextureNameList
        cls.TEXTURE_NAME = TextureName
        cls.INDEX_TEXTURE = IndexTexture

    @classmethod
    def unload(cls):
        cls.TEXTURE_SET = None
        cls.TEXTURE_NAME_LIST = None
        cls.TEXTURE_NAME = None
        cls.INDEX_TEXTURE = None
