
'''Info Header Start
Name : tweenerTest
Author : Wieland PlusPlusOne@AMB-ZEPH15
Saveorigin : TauCeti_PresetSystem.toe
Saveversion : 2023.12000
Info Header End'''

# Imports
from asyncio import sleep
from typing import cast, Union, TYPE_CHECKING, Any

# Recommend using the TYPE_CHECKING route here 
if TYPE_CHECKING:   
    from TauCeti.Tweener.extTweener import extTweener
else:
    extTweener = Any

# Typing Definitions

class TestParDef:
    Float1: Par
    Float2: Par

class TestComp:
    par : TestParDef

tweener = cast( extTweener, op("Tweener") )
parComp = cast( Union[TestComp, COMP], op("parameter1") )

# Test Routine

async def naiveTweenerTest():
    parComp.par.Float1.val = 0
    parComp.par.Float2.val = 0
    # Test awaitability
    
    await tweener.AbsoluteTween(
        parComp.par.Float1,
        1,
        1
    ).Resolve()

    assert parComp.par.Float1.eval() == 1
    
    await tweener.RelativeTween(
        parComp.par.Float2,
        1,
        1
    ).Resolve()

    assert parComp.par.Float2.eval() == 1
    

    tweener.AbsoluteTweens(
        [
            { "par" : parComp.par.Float1, "end" : 0},
            { "par" : parComp.par.Float2, "end" : 0, "time" : 2}
        ],
        time = 1
    )
    await sleep(2)
    assert parComp.par.Float1.eval() == 0 and  parComp.par.Float2.eval() == 0
    
    
     
    tweener.RelativeTweens(
        [
            { "par" : parComp.par.Float1, "end" : 1},
            { "par" : parComp.par.Float2, "end" : 1, "speed" : 2}
        ],
        speed = 1
    )
    await sleep(1)

    assert parComp.par.Float1.eval() == 1 and  parComp.par.Float2.eval() == 1
    
# Execute Routine

op("TDAsyncIO").Run( naiveTweenerTest() )  # type: ignore