'''Info Header Start
Name : extCurve
Author : Wieland PlusPlusOne@AMB-ZEPH15
Saveorigin : TauCeti_PresetSystem.toe
Saveversion : 2025.32460
Info Header End'''
import math
TDF = op.TDModules.mod.TDFunctions

class extCurve:

	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		
		self.curves 	 = self.ownerComp.op("curves")
		self.default 	 = "LinearInterpolation"

	@property
	def Curves(self):
		return [ channel.name for channel in self.curves.chans() ]

	def Get_Curve(self, target):
		channel = self.curves[target]
		if channel is None: return self.curves[self.default]
		return self.curves[target] 

	def GetValue(self, index, range, target):
		
		channel = self.Get_Curve( target )
		
		chopIndex = tdu.remap(index, 0, range, 0, self.curves.numSamples - 1) 
		chopIndex = tdu.clamp( chopIndex, 0, self.curves.numSamples - 1 )
		topIndex = math.ceil(chopIndex)
		bottomIndex = math.floor(chopIndex)
		weight = chopIndex - bottomIndex
		
		topValue = channel[topIndex] *  (weight)
		bottomValue = channel[bottomIndex] * (1.0 - weight)
		
		return topValue + bottomValue

			
		