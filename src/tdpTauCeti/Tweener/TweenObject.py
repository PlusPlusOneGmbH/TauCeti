

'''Info Header Start
Name : fade
Author : Wieland PlusPlusOne@AMB-ZEPH15
Saveorigin : TauCeti_PresetSystem.toe
Saveversion : 2023.12000
Info Header End'''

from td import *
if __package__ is None:
	import TweenValue
else: 
	from . import TweenValue



from dataclasses import dataclass, field
from asyncio import sleep as asyncSleep

from typing import Callable, List, Union, Hashable
from abc import ABCMeta, abstractmethod

@dataclass
class _tween(metaclass = ABCMeta):
	"""
		A tween component being used to programatically move between parameter states.
		Cntrolled via the TweenerCOMP Extension.
	"""
	parameter		:	Par
	TweenerCOMP		: 	COMP
	time			:   float
	startValue		:	TweenValue._tweenValue
	targetValue		:   TweenValue._tweenValue
	interpolation	:	str 			= "LinearInterpolation"
	id				:	Hashable		= ""
	_currentStep	:	float 			= field( default= 0, repr=False)

	Active			:	bool			= True
	OnDoneCallbacks :   List[Callable] 	= field( default_factory = list)
	
	@abstractmethod
	def Step(self, stepsize:Union[float, None] = None):
		pass
	
	@abstractmethod
	def Finish(self):
		pass
		
	
	def _incrementStep(self, stepsize:Union[float, None]):
		stepsize = stepsize or absTime.stepSeconds
		self._currentStep += stepsize
		#self.current_step = tdu.clamp( self.current_step + stepsize, 0, self.time )

	@property
	def done(self):
		return self._currentStep >= self.time
	
	@property
	def Done(self):
		""" True if the Tween is done and will not continue. """
		return self.done
	
	@property
	def Remaining(self) -> float:
		""" Returns the remaining seconds of the tween until completion. """
		return self.time - self._currentStep
	
	def Pause(self):
		""" Halts the continuation of the tween untils resumed."""
		self.Active = False

	def Resume(self):
		""" Continues to tween."""
		self.Active = True

	def Stop(self):
		""" Tops the tween right where it is and removes it. """
		self.TweenerCOMP.StopTween(self) # type: ignore   Circular Refference, so this has to stay.


	def Reset(self):
		""" Return to to the initital value and clean up."""
		self.targetValue = self.startValue
		self.Finish()

	def Reverse(self):
		""" Changes target and startingpoint mid flight. """
		_startValue = self.startValue
		self.startValue = self.targetValue
		self.targetValue = _startValue

	def Delay(self, offset:float):
		""" Reduces the current ime by offset. When at 0, this results in a delay, when above 0 will result in a stepback. """
		self._currentStep -= abs(offset)


	async def Resolve(self):
		""" Async Awaitable for finisshing up."""
		while not self.done:
			await asyncSleep(0)
		return


class fade( _tween ):
	def Step(self, stepsize = None):
		self._incrementStep(stepsize)

		curves 				= me.parent.TWEENER.op("curves_repo").Repo # type: ignore Until I have proper package management this has to be taken for granted.
		# why do I have to do that? This feels strange.
		# is this because of my hack?

		curve_value 		= curves.GetValue( self._currentStep, self.time, self.interpolation )
		start_evaluated:float	= self.startValue.eval()
		target_evaluated:float 	= self.targetValue.eval()
		difference 			= target_evaluated - start_evaluated
		new_value 			= start_evaluated + difference * curve_value
		self.parameter.val = new_value
		if self.done: self.Finish()

	def Finish(self):
		self.targetValue.assignToPar( self.parameter )
		for callback in self.OnDoneCallbacks:
			callback( self )


class endsnap( _tween ):

	def Step(self, stepsize = None):
		
		self._incrementStep(stepsize)
		if self.done: self.Finish()

	def Finish(self):
		self.targetValue.assignToPar( self.parameter )
		for callback in self.OnDoneCallbacks:
			callback( self )


class startsnap( _tween ):

	def Step(self, stepsize = None):
		self.targetValue.assignToPar( self.parameter )
		self._incrementStep(stepsize)
		if self.done: self.Finish()

	def Finish(self):
		for callback in self.OnDoneCallbacks:
			callback( self )
