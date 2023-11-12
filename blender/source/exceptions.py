class UserException(Exception):

    message: str

    def __init__(self, message: str, *args: object):
        self.message = message
        super().__init__(message, *args)


class SAIOException(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
