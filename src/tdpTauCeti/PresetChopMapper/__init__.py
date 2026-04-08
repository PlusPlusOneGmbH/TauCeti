'''Info Header Start
Name : __init__
Author : Wieland PlusPlusOne@AMB-ZEPH15
Saveorigin : TauCeti_PresetSystem.toe
Saveversion : 2025.32460
Info Header End'''

from pathlib import Path
ToxFile = Path( Path(  __file__ ).parent, "PresetChopMapper.tox" )
DefaultGlobalOpShortcut = "TAUCETI_PRESETCHOPMAPPER"


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    class Typing(baseCOMP):
        pass
else:
    Typing = None

__all__ = ["ToxFile", "Typing"]
