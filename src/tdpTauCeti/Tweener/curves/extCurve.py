'''Info Header Start
Name : extCurve
Author : wieland@plusplus.one
Saveorigin : TauCeti_PresetSystem.toe
Saveversion : 2025.32460
Info Header End'''

import math
TDF = op.TDModules.mod.TDFunctions


from typing import Literal

available_curves = Literal[
	"LinearInterpolation","QuadraticEaseIn","QuadraticEaseOut","QuadraticEaseInOut",
	"CubicEaseIn","CubicEaseOut","CubicEaseInOut","QuarticEaseIn","QuarticEaseOut",
	"QuarticEaseInOut","QuinticEaseIn","QuinticEaseOut","SineEaseIn","SineEaseOut",
	"SineEaseInOut","CircularEaseIn","CircularEaseOut","CircularEaseInOut",
	"ExponentialEaseIn","ExponentialEaseOut","ExponentialEaseInOut","ElasticEaseIn",
	"ElasticEaseOut","ElasticEaseInOut","BackEaseIn","BackEaseOut","BackEaseInOut",
	"BounceEaseIn","BounceEaseOut","BounceEaseInOut", "s"
]



class extCurve:

	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		
		self.curves 	 = self.ownerComp.op("curves")
		self.default 	 = "LinearInterpolation"

	@property
	def Curves(self):
		return [ channel.name for channel in self.curves.chans() ]

	def Get_Curve(self, target:available_curves):
		channel = self.curves[target]
		if channel is None: return self.curves[self.default]
		return self.curves[target] 

	def GetValue(self, index:float, range, target:available_curves):
		
		channel = self.Get_Curve( target )
		
		chopIndex = tdu.remap(index, 0, range, 0, self.curves.numSamples - 1) 
		chopIndex = tdu.clamp( chopIndex, 0, self.curves.numSamples - 1 )
		topIndex = math.ceil(chopIndex)
		bottomIndex = math.floor(chopIndex)
		weight = chopIndex - bottomIndex
		
		topValue = channel[topIndex] *  (weight)
		bottomValue = channel[bottomIndex] * (1.0 - weight)
		
		return topValue + bottomValue

			
		