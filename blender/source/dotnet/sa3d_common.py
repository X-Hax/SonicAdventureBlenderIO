class SA3D_Common:
    '''SA3D.Common library types'''

    LABELED_ARRAY: any = None
    '''Class SA3D.Common.Lookup.LabeledArray<T>'''

    @classmethod
    def load(cls):
        from SA3D.Common.Lookup import (  # pylint: disable=import-error
            LabeledArray
        )

        cls.LABELED_ARRAY = LabeledArray

    @classmethod
    def unload(cls):
        cls.LABELED_ARRAY = None
