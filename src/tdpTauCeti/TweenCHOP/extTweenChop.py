'''Info Header Start
Name : extTweenChop
Author : wieland@plusplus.one
Saveorigin : TauCeti_PresetSystem.toe
Saveversion : 2025.32460
Info Header End'''

from touchutilcollection.ensure import ensure_global_tdp
from tdpTauCeti import Tweener

class extTweenChop:
	"""
	extTweenChop description
	"""
	def __init__(self, ownerComp:baseCOMP):
		# The component to which this extension is attached
		self.ownerComp = ownerComp

		self.constant = self.ownerComp.opex("constant1").asType( constantCHOP )
		self.Reset()
		self.Tweener = ensure_global_tdp( Tweener, cast_as = Tweener.Typing )

	@property
	def CurvesParMenu(self):
		return tdu.ParMenu(
			self.Tweener.op("curves").Curves
		)

	def Reset(self):
		self.constant.seq.const.numBlocks = self.ownerComp.seq.Channels.numBlocks
		for index, block in enumerate( self.ownerComp.seq.Channels ):
			self.constant.seq.const[index].par.value.val = block.par.Target.eval()
			self.constant.seq.const[index].par.name.expr = "parent().seq.Channels[me.curPar.sequenceBlock.index].par.Name.eval()"

	def TriggerTween(self, index:int):
		block = self.ownerComp.seq.Channels[index]
		if block.par.Mode.eval() == "Absolute":
			self.Tweener.AbsoluteTween( 
				self.constant.seq.const[index].par.value,
				block.par.Target.eval(),
				block.par.Timespeed.eval(),
				curve = block.par.Curve.eval()
			  )
		else:
			self.Tweener.RelativeTween( 
				self.constant.seq.const[index].par.value,
				block.par.Target.eval(),
				block.par.Timespeed.eval(),
				curve = block.par.Curve.eval()
			  )