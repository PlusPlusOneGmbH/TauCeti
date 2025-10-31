

'''Info Header Start
Name : tween_value
Author : Wieland PlusPlusOne@AMB-ZEPH15
Saveorigin : TauCeti_PresetSystem.toe
Saveversion : 2023.12000
Info Header End'''
from td import *
if __package__ is None:
    import Exceptions
else:
    from . import Exceptions

from functools import lru_cache
from typing import Union
from abc import abstractmethod, ABCMeta
from enum import Enum

# Where does this come from?
class ParMode(Enum):
    BIND = "BIND"
    CONSTANT = "CONSTANT"
    EXPORT = "EXPORT"
    EXPRESSION = "EXPRESSION"

par_modes = [parmode.name.upper() for parmode in ParMode._value2member_map_.values()]
TweenableValue = Union[int, float]


@lru_cache(maxsize=None)
def getParamaterTypecast(parameter):
    if parameter.style  == "Pulse": return bool
    if parameter.style == "Toggle": return lambda value: bool(float(value))
    return type( parameter.val )

class _tweenValue(metaclass = ABCMeta):
    @abstractmethod
    def eval(self) -> float:
        pass
    
    @abstractmethod
    def assignToPar(self, parameter:Par):
        pass

class ExpressionValue( _tweenValue ):
    def __init__(self, parameter:Par , expression_string:str):
        self.expressionString = expression_string
        self.expressionFunction = lambda : parameter.owner.evalExpression( expression_string )
    
    def eval(self):
        return self.expressionFunction()

    def assignToPar(self, parameter:Par):
        parameter.mode = ParMode.EXPRESSION
        parameter.expr = self.expressionString
        

class StaticValue( _tweenValue ):
    def __init__(self, parameter:Par, value:TweenableValue):
        self.value = getParamaterTypecast( parameter )(value)

    def eval(self):
        return self.value

    def assignToPar(self, parameter:Par):
        parameter.val = self.eval()



@lru_cache(None)
def stringifyParmode( mode:ParMode ):
    if isinstance(mode, ParMode): return mode.name.upper()
    if isinstance(mode, str) and mode.upper() in par_modes: return mode.upper()
    raise Exceptions.InvalidParMode

def tweenValueFromParameter( parameter:Par ):
    if parameter.mode.name =="EXPRESSION": return ExpressionValue( parameter, parameter.expr ) # type: ignore WTF, why does it think the classInstanciator takes 2 arguments?
    return StaticValue( parameter, parameter.eval() ) # type: ignore

def tweenValueFromArguments( parameter:Par, mode:Union[str, ParMode], expression:Union[str, None], value:TweenableValue):
    if stringifyParmode(mode) =="EXPRESSION" and expression: return ExpressionValue( parameter, expression ) # type: ignore
    return StaticValue( parameter, value ) # type: ignore
    

