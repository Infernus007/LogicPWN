class ConnectionClosed(Exception):
    def __init__(self, code=1000, reason=""):
        super().__init__(reason)
        self.code = code


class InvalidURI(Exception):
    pass
