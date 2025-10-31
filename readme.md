# TauCeti PresetSystem + Tweener
Highly customisable and setup agnostic system for presets management in TouchDesigner

## Installation

You can download standalone ToxFiles from the the dist-folders of the repository. Choose the specific branch for the correct version.

### PIP Installation

This project implements ideas and features of TD_Package, a proposal by PlusPlusOne on how to create shareable components as python packages. This means, you can install this project via PIP and gain access to automated updates and code compleation.

All modules (PresetManager and Tweener) implement the ToxFile member. Refference the ToxFile in the external-parameter of any COMP and force a reload.

```mod.tdpTauCeti.Tweener.ToxFile```
will return the path to the ToxFile.

For easy code compleation in your IDE use the exported Typying member of the module.
```python
from tdpTauCeti.Tweener import Typing as TweenerTyping

tweener_comp:TweenerTyping = op("Tweener")
```
Typing is only importing and evaluating during TYPE_CHECKING and evaluates to NONE during runtime.



## Note on Versions
This project uses SemVer. All releases of a major version will be fully compatible. Minor releases will only add new features. Patches should not change behaviour.

## Contributing
This project is released under the GPL-3.0 license and part of PlusPlusOne FOSS projects.
Feel free to open pull requests or open issues.

## Tweener
The tweener is the heart of the whole system and a great component in itself. It allows for programmatic creation and management of Tweens, transitions between states of a parameter. Be it Expression or Static, fadeable and non-fadeable parameters, the Tweener should be able to handle them.

__ There should only be one tweener per project. Use GlobalOP-Shortcuts or other means of dependency management __


The tweener offers several ways of creating tweens. All do wrap arround CreateTween as the most important method.
```python
op("Tweener").AbsoluteTween(	   
					parameter : Par, 
					targetValue : any, 
					time : float, 
					curve : str            = "LinearInterpolation", 
					delay : float          = 0, 
					callback : Callable    = _emptyCallback ) -> TweenObject
# Creates a tween that will resolve in the defines time.

op("Tweener").RelativeTween( 
				   parameter:Par, 
				   targetValue:any, 
				   speed:float, 
				   curve:str            = "LinearInterpolation", 
				   delay:float          = 0, 
				   callback: Callable   = _emptyCallback) -> TweenObject
# Creates a Tween that will resolve with the given speed in distance per seconds.

```

Both functions are clearly aimed at fadeable, meaning numeric, parameters. They will fail for non-numeric values.

For nun-numeric parameters the underlying CreateTween is required.
```python
op("Tweener"):CreateTween(
					parameter :Par, 
					targetValue	:float, 
					time	:float, 
					type	:Literal["fade", "startsnap", "endsnap"] = 'fade', 
					curve	:str				= "LinearInterpolation", 
					mode	:Union[str, ParMode]= 'CONSTANT', 
					expression	:str			= None, 
					delay		:float			= 0.0,
					callback	:Callable		= _emptyCallback,
					id		:Hashable			= '',  ) -> TweenObject:
# Creates a Tween for the given paramaters.
# If mode is set to ParMode.EXPRESSION, the targetValue will be ignored and expression wil be used instead.
```

calback is a function that takes a single arguments in form of the TweenObject.

The TweenObject has the following attributes and methods:

```python
Active : bool # If False, the tween will not be continued until Active is back to True
OnDoneCallbacks : List[Callable] # A list of callales that will be executed once the tween is done.
Done : bool # True if the Tween is done.
Remaining : float # seconds left unti complition.

Pause() # Halts the continuation of the tween untils resumed.
Resume() # Continues the tween.
Stop() # Stops the tween right where it is and removes it. 
Reset() # Reverses all changes done by the tween and stops it.
Reverse() # Changes target and startingpoint mid flight. 
Delay(offset:float) # Reduces the current ime by offset. When at 0, this results in a delay, when above 0 will result in a stepback.

Resolve() #  In async context, await the compleation of the tween, then conitnue.
```


The Tweener itself also offers some additional utility functions.
```python
StopTween( target: Union[Par, TweenObject._tween]) # Stops a tween by the tween object or the parameter wich it points to.
StopAllFades() # Does exactly what it sais it does. Should be named StopAllTweens though. 
Tweens : Dict[int, TweenObject] # A dict containing all tweens, keyed by an unique ID per parameter.
TweensByOp( targetOpartor:OP) # Returns a list of all tweens that are running and pointing at a prameter of the given operator.
```

### Example
Fading in a levelTOP in 1 second.
```python
op("Tweener").AbsoluteTween( op("level1").par.opacity, 1, 1)
```

Awaiting the completion of a tween.
```python
await op("Tweener").AbsoluteTween( op("level1").par.opacity, 1, 1).Resolve()
```

Transition from current value to a refference of an LFO.
```python
op("Tweener").CreateTween(
	op("level1").par.opacity, None, 1, 
	mode = ParMode.EXPRESSION,
	expr = "op('lfo1')['chan1']"
)
```

A pretty destructive tween.
```python
def callback( tweenObject ):
	tweenObject.Paramater.owner.destroy()
	
tweenObject = op("Tweener").AbsoluteTween( op("level1").par.opacity, 1, 1)
tweenObject.OnDoneCallbacks.append( callback )
```
## PresetManager
The presetmanager allows to store and recall state of any arbitrary parameters.

Most operations will use the stack, which is a collection of parameters. To add any parameter to the stack, activate the viewer and add drop the parameter right in.

This video contains most information required for the operation: 
https://www.youtube.com/watch?v=SSNvsvrnifI

### DataRepository
The presetmanager holds all data in so called Repositories: Components that only hold data and do not enact any functionality. These components can be placed outside of the PresetManager, allowing for a seperation of the PresetManager and the dataset, allowing for super easy updates or transition between environments.

### Fademodes
There are three fademodes. 
- Startsnap: Will set the value in 0 seconds when the preset gets recalled.
- Endsnap: Will set the vaue in 0 seconds once the transition to the new preset is done.
- Fade: Smoothly transition between states. Only for numeric parameters.

### Preloading
Marks the parameter to be preloadable. A call to the ```Preload( preset_id )``` method of the presetManager will set it to the stored value witout triggering any transition or non marked parameters.

This could be used to set colorvalue before fading in. 


To be added:
- Parameter
- Python API