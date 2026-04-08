'''Info Header Start
Name : __init__
Author : Wieland PlusPlusOne@AMB-ZEPH15
Saveorigin : TauCeti_PresetSystem.toe
Saveversion : 2025.32460
Info Header End'''

from pathlib import Path
ToxFile = Path( Path(  __file__ ).parent, "PresetDashboard.tox" )
DefaultGlobalOpShortcut = "TAUCETI_PRESETDASHBOARD"


from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:

    from .extDashboard import extDashboard
    class Typing( containerCOMP, extDashboard):
        pass
else:
    class Typing:
        pass

__all__ = ["ToxFile", "Typing"]
