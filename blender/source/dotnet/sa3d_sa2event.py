class SA3D_SA2Event:
    '''SA3D.SA2Event library types'''

    EVENT: any = None
    '''Class SA3D.SA2Event.Event'''

    EVENT_TYPE: any = None
    '''Enum SA3D.SA2Event.EventType'''

    MODEL_DATA: any = None
    '''Class SA3D.SA2Event.Model.ModelData'''

    SCENE: any = None
    '''Class SA3D.SA2Event.Model.Scene'''

    EVENT_ENTRY: any = None
    '''Class SA3D.SA2Event.Model.EventEntry'''

    BIG_THE_CAT_ENTRY: any = None
    '''Class SA3D.SA2Event.Model.BigTheCatEntry'''

    REFLECTION_DATA: any = None
    '''Class SA3D.SA2Event.Model.ReflectionData'''

    REFLECTION: any = None
    '''Struct SA3D.SA2Event.Model.Reflection'''

    EVENT_MOTION: any = None
    '''Struct SA3D.SA2Event.Animation.EventMotion'''

    SURFACE_ANIMATION_DATA: any = None
    '''Class SA3D.SA2Event.Animation.SurfaceAnimationData'''

    SURFACE_ANIMATION_BLOCK: any = None
    '''Class SA3D.SA2Event.Animation.SurfaceAnimationBlock'''

    SURFACE_ANIMATION: any = None
    '''Class SA3D.SA2Event.Animation.SurfaceAnimation'''

    TEXTURE_ANIM_SEQUENCE: any = None
    '''Struct SA3D.SA2Event.Animation.TextureAnimSequence'''

    @classmethod
    def load(cls):

        from SA3D.SA2Event import (  # pylint: disable=import-error
            Event,
            EventType,
        )

        from SA3D.SA2Event.Model import (  # pylint: disable=import-error
            ModelData,
            Scene,
            EventEntry,
            BigTheCatEntry,
            ReflectionData,
            Reflection,
        )

        from SA3D.SA2Event.Animation import (  # pylint: disable=import-error
            EventMotion,
            SurfaceAnimationData,
            SurfaceAnimationBlock,
            SurfaceAnimation,
            TextureAnimSequence,
        )

        cls.EVENT = Event
        cls.EVENT_TYPE = EventType
        cls.MODEL_DATA = ModelData
        cls.SCENE = Scene
        cls.EVENT_ENTRY = EventEntry
        cls.BIG_THE_CAT_ENTRY = BigTheCatEntry
        cls.REFLECTION_DATA = ReflectionData
        cls.REFLECTION = Reflection
        cls.EVENT_MOTION = EventMotion
        cls.SURFACE_ANIMATION_DATA = SurfaceAnimationData
        cls.SURFACE_ANIMATION_BLOCK = SurfaceAnimationBlock
        cls.SURFACE_ANIMATION = SurfaceAnimation
        cls.TEXTURE_ANIM_SEQUENCE = TextureAnimSequence

    @classmethod
    def unload(cls):
        cls.EVENT = None
        cls.EVENT_TYPE = None
        cls.MODEL_DATA = None
        cls.SCENE = None
        cls.EVENT_ENTRY = None
        cls.BIG_THE_CAT_ENTRY = None
        cls.REFLECTION_DATA = None
        cls.REFLECTION = None
        cls.EVENT_MOTION = None
        cls.SURFACE_ANIMATION_DATA = None
        cls.SURFACE_ANIMATION_BLOCK = None
        cls.SURFACE_ANIMATION = None
        cls.TEXTURE_ANIM_SEQUENCE = None
