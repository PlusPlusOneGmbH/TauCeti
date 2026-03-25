'''Info Header Start
Name : __init__
Author : Wieland PlusPlusOne@AMB-ZEPH15
Saveorigin : TauCeti_PresetSystem.toe
Saveversion : 2023.12000
Info Header End'''
from pathlib import Path
ToxFile = Path( Path(  __file__ ).parent, "Tweener.tox" )
DefaultGlobalOpShortcut = "TAUCETI_TWEENER"


from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from .extTweener import extTweener
    class typing(baseCOMP, extTweener):
        pass
else:
    Typing = None

__all__ = ["ToxFile", "Typing"]