class IllegalActionException(Exception):
    """Represents moves that are illegal in the game rule framework
    """
    def __init__(self, *args):
        super().__init__(*args)

class MissingResourceException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class InvalidDataException(Exception):
    def __init__(self, *args):
        super().__init__(*args)