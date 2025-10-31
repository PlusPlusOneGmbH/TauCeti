




'''Info Header Start
Name : extTweener
Author : Wieland PlusPlusOne@AMB-ZEPH15
Saveorigin : TauCeti_PresetSystem.toe
Saveversion : 2023.12000
Info Header End'''

from td import *
# TD specific import shenaningans.
if __package__ is None:
	import TweenObject
	import TweenValue
	import Exceptions
	from TweenValue import TweenableValue
else:
	from . import TweenObject
	from . import TweenValue
	from . import Exceptions
	from .TweenValue import TweenableValue

from asyncio import sleep as asyncSleep

from typing import Callable, Union, Hashable, Dict, List, Literal, Type, TypedDict, NotRequired, cast
from argparse import Namespace




def _emptyCallback( value:TweenObject._tween ):
	pass

_type = type
PotentialCurves = Union[ str, Literal["s", "LinearInterpolation", "QuadraticEaseIn", "QuadraticEaseOut", "BackEaseIn", "BounceEaseIn"] ]



class AbsoluteTweenDefinition(TypedDict):
	par			: Par
	end			: TweenableValue
	time 		: NotRequired[float]
	curve 		: NotRequired[PotentialCurves]
	delay 		: NotRequired[float]
	callback 	: NotRequired[Callable]

class RelativeeTweenDefinition(TypedDict):
	par			: Par
	end			: TweenableValue
	speed 		: NotRequired[float]
	curve 		: NotRequired[PotentialCurves]
	delay 		: NotRequired[float]
	callback 	: NotRequired[Callable]


class extTweener:

	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp 						= ownerComp
		self.Tweens:Dict[int, TweenObject._tween] 	= {}

		self.Modules = Namespace(
			Exceptions 	= Exceptions
		)
		self.Constructor = Namespace(
			Expression 	= TweenValue.ExpressionValue,
			Static 		= TweenValue.StaticValue,
			FromPar		= TweenValue.tweenValueFromParameter
		)
		self.callback 	= self.ownerComp.op('callbackManager')

		# Bacwards compatible stuff. 
		# CLearer naming conventions.

		self.StopFade 	= self.StopTween
		self.getFadeId  = self.getTweenId
		self.FadeStep	= self.TweenStep
		self.StopAllFades = self.StopAllTweens

	def getTweenId(self, parameter:Par):
		return hash(parameter)

	def TweenStep(self, step_in_ms = None):
		"""
			Progresses all active tweens for the given time. 
			Should be called from the internal clock but can be also run from an external source if wished.
		"""
		fadesCopy = self.Tweens.copy()
		for fade_id, tween_object in fadesCopy.items():
			if not tween_object.Active: continue
			tween_object.Step(step_in_ms)
			if tween_object.done: del self.Tweens[ fade_id ]
		

	def AbsoluteTweens(self, listOfTweenDefinition:List[AbsoluteTweenDefinition], curve:PotentialCurves	= "s", time 	= 1) -> List[TweenObject._tween]:
		"""
			Calls AbsoluteTween for each element of the given List of dicts
			which needs at least par and end memeber. otional time, curve, delay nd callback
		"""
		return [
			self.AbsoluteTween( 
				tweenDict["par"], 
				tweenDict["end"], 
				tweenDict.get("time", time), 
				curve = tweenDict.get("curve", None) or curve,
				delay = tweenDict.get("delay", 0), 
				callback= tweenDict.get("callback", None) or _emptyCallback,
			)
			for tweenDict in listOfTweenDefinition 
		]
			

	def RelativeTweens(self, listOfTweenDefinition : List[RelativeeTweenDefinition], curve:PotentialCurves 	= "s", speed	= 1):
		"""
			Calls AbsoluteTween for each element of the given List of dicts
			which needs at least par and end memeber. otional time, curve, delay nd callback
		"""
		return [
			self.RelativeTween( 
				tweenDict["par"], 
				tweenDict["end"], 
				tweenDict.get("speed", speed), 
				curve = tweenDict.get("curve", None) or curve,
				delay = tweenDict.get("delay", 0),
				callback= tweenDict.get("callback", None) or _emptyCallback,
			)
			for tweenDict in listOfTweenDefinition 
		]
	
	def AbsoluteTween(self, 
					parameter:Par, 
					end:TweenableValue, 
					time:float, 
					curve:PotentialCurves = "LinearInterpolation", 
					delay:float = 0, 
					callback: Callable = _emptyCallback) -> TweenObject._tween:
		"""
			Creates a tween that will resolve in the defines time.
		"""
		return self.CreateTween(parameter, end, time, curve = curve, delay = delay, callback = callback)
		

	def RelativeTween(self, 
					parameter:Par, 
					end:TweenableValue, 
					speed:float, 
					curve:PotentialCurves = "LinearInterpolation", 
					delay:float = 0, 
					callback: Callable = _emptyCallback) -> TweenObject._tween:
		"""
			Creates a tween that will resolve with the given peed ( value increment per seconds )
		"""
		difference = abs(end - parameter.eval())
		time = difference / speed
		return self.CreateTween(parameter, end, time, curve = curve, delay = delay, callback = callback)
		

	def CreateTween(self,parameter, 
					end		:TweenableValue, 
					time	:float, 
					type	:Literal["fade", "startsnap", "endsnap"] = 'fade', 
					curve	:PotentialCurves	= "LinearInterpolation", 
					mode	:Union[str, ParMode]= 'CONSTANT', 
					expression	:Union[str, None] = None, 
					delay		:float			= 0.0,
					callback	:Callable		= _emptyCallback,
					id		:Hashable			= '',  ) -> TweenObject._tween:
		"""
			Creates the given tween object based on the definition. 
		"""
		if not isinstance( parameter, Par):
			raise Exceptions.TargetIsNotParameter(f"Invalid Parameterobject {parameter}")
		

		if isinstance( parameter.default, (int, float)):
			end = float( end ) # If we get a str value (or similiar) as the target value, we can make sure that we are fading non the less. Not perfect :()


		targetValue	:TweenValue._tweenValue 	= TweenValue.tweenValueFromArguments( parameter, mode, expression, end )
		startValue	:TweenValue._tweenValue 	= TweenValue.tweenValueFromParameter( parameter )

		tweenClass: Type[TweenObject._tween]	 = getattr( TweenObject, type, TweenObject.startsnap )

		tweenOject 	= tweenClass( 
			parameter, 
			self.ownerComp,
			time, 
			startValue, 
			targetValue, 
			interpolation = curve, 
			id = id
		)
		tweenOject.OnDoneCallbacks.append( callback or _emptyCallback ) 
		
		tweenOject.Delay( delay )
		self.Tweens[self.getTweenId( parameter )] = tweenOject

		tweenOject.Step( stepsize = 0 )

		return tweenOject
		

	def StopTween(self, target: Union[Par, TweenObject._tween]):
		""" Stops a tween by the tween object or the parameter wich it points to. """
		if isinstance( target, TweenObject._tween):
			target = target.parameter
			
		del self.Tweens[self.getTweenId(target)]

	def StopAllTweens(self):
		""" Stops all tweens."""
		self.Tweens = {}

	def ClearFades(self):
		self.Tweens.clear()

	def PrintFades(self):
		raise DeprecationWarning("Yeah, please dont.")

	def TweensByOp(self, targetOp:OP):
		""" Return all Tweens filtered by the given operator. """
		return {
			key : tween for key, tween in self.Tweens.items() if tween.parameter.owner == targetOp
		}