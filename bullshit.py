#* improved annotations
from typing import Any, Literal, NoReturn
from __future__ import annotations

class Bullshit:
    '''
    Base class for all failures (exceptions). Analog of BaseException class in Python.
    '''
    def __init__(self, message= "unknown kinda bullshit"):
        self.content = message

    def __str__(self) -> str:
        return f"\033[31mSOME SHIT HAPPENED!!!!\n\t{self.__class__.__name__}: {self.content}\033[0m"

class OhGodDamnOKBullshit(Bullshit):
    '''
    Base class for all "normal" failures. Analog of Exception in Python
    '''
    def __init__(self, message= "unknown kinda bullshit" ):
        super().__init__(message)

class SyntaxFailure(OhGodDamnOKBullshit):
    def __init__(self, message="unknown kinda bullshit"):
        super().__init__(message)
    
    def __str__(self):
        return super().__str__()
    
class TypeFailure(OhGodDamnOKBullshit):
    def __init__(self, message="unknown kinda bullshit"):
        super().__init__(message)

    def __str__(self):
        return super().__str__()

class SickBullshit(Bullshit):
    '''
    Base class for all unbound exceptions like ConsoleInterrupt.
    '''
    def __init__(self, message="unknown kinda bullshit"):
        super().__init__(message)


class ConsoleInterrupt(SickBullshit):
    def __init__(self, message="unknown kinda bullshit"):
        super().__init__(message)

    def __str__(self):
        return super().__str__()