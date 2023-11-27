class SA3D_Archival:
    '''SA3D.Archival library types'''

    ARCHIVE: any = None
    '''Class SA3D.Archival.Archive'''

    PRS: any = None
    '''Class SA3D.Archival.PRS'''

    PAK_ARCHIVE: any = None
    '''Class SA3D.Archival.PAK.PAKArchive'''

    PVMX: any = None
    '''Class SA3D.Archival.Tex.PVX.PVMX'''

    PVM: any = None
    '''Class SA3D.Archival.Tex.PV.PVM'''

    GVM: any = None
    '''Class SA3D.Archival.Tex.GV.GVM'''

    @classmethod
    def load(cls):
        from SA3D.Archival import (  # pylint: disable=import-error
            Archive,
            PRS,
        )
        from SA3D.Archival.PAK import PAKArchive  # pylint: disable=import-error
        from SA3D.Archival.Tex.PVX import PVMX  # pylint: disable=import-error
        from SA3D.Archival.Tex.PV import PVM  # pylint: disable=import-error
        from SA3D.Archival.Tex.GV import GVM  # pylint: disable=import-error

        cls.ARCHIVE = Archive
        cls.PRS = PRS
        cls.PAK_ARCHIVE = PAKArchive
        cls.PVMX = PVMX
        cls.PVM = PVM
        cls.GVM = GVM

    @classmethod
    def unload(cls):
        cls.ARCHIVE = None
        cls.PRS = None
        cls.PAK_ARCHIVE = None
        cls.PVMX = None
        cls.PVM = None
        cls.GVM = None
