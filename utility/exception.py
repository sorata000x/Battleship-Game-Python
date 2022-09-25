"""
Reference
    Proper way to declare custom exceptions in modern Python?
        https://stackoverflow.com/questions/1319615/proper-way-to-declare-custom-exceptions-in-modern-python
"""

class ShipPositionException(Exception):
    """ exception for incorrect ship positions """
    def __init__(self, message):
        super().__init__(message)
