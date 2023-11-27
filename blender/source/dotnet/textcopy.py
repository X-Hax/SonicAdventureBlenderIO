
class TextCopy:

    CLIPBOARD_SERVICE: any = None
    '''Class TextCopy.ClipboardService'''

    @classmethod
    def load(cls):
        from TextCopy import ClipboardService # pylint: disable=import-error

        cls.CLIPBOARD_SERVICE = ClipboardService

    @classmethod
    def unload(cls):
        cls.CLIPBOARD_SERVICE = None
