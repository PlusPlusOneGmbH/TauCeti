'''Info Header Start
Name : __init__
Author : Wieland PlusPlusOne@AMB-ZEPH15
Saveorigin : TauCeti_PresetSystem.toe
Saveversion : 2023.12480
Info Header End'''

from pathlib import Path
ToxFile = Path( Path(  __file__ ).parent, "PresetCuelist.tox" )
DefaultGlobalOpShortcut = "TAUCETI_CUELIST"


from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from .extCuelist import extCuelist
    Typing = Union[
        extCuelist
    ]
else:
    Typing = None

__all__ = ["ToxFile", "Typing"]
