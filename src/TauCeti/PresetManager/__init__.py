'''Info Header Start
Name : __init__
Author : Wieland PlusPlusOne@AMB-ZEPH15
Saveorigin : TauCeti_PresetSystem.toe
Saveversion : 2023.12000
Info Header End'''
from pathlib import Path
ToxFile = Path( Path(  __file__ ).parent, "PresetManager.tox" )
DefaultGlobalOpShortcut = "TAUCETI_PRESETMANAGER"


from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from .extParStack import extParStack
    from .extTauCetiManager import extTauCetiManager
    Typing = Union[
        extParStack, extTauCetiManager
    ]
else:
    Typing = None

__all__ = ["ToxFile", "Typing"]
