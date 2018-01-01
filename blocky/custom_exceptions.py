class CarryOnException(Exception):
    """Exceptions that SHOULD NOT CRASH THE GAME ENGINE
       Illegal moves, etc
    """
    def __init__(self, *args):
        super().__init__(*args)

class CriticalException(Exception):
    pass



class IllegalActionException(CarryOnException):
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

class TempException(Exception):
    def __init__(self, *args):
        super().__init__(*args)        