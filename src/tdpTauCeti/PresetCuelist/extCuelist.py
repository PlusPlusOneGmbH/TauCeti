'''Info Header Start
Name : extCuelist
Author : Wieland PlusPlusOne@AMB-ZEPH15
Saveorigin : TauCeti_PresetSystem.toe
Saveversion : 2023.12480
Info Header End'''


class extCuelist:
	"""
	extCuelist description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		#self.cue_table = self.ownerComp.op('cuelist')
		
		# if self.ownerComp.par.Manager.eval() is not None: self.Recall_Cue( "", time = 0 )
	
	@property
	def MenuDefinition(self):

		return tdu.ParMenu( [ 
			f"{block.index} : {block.par.Name.eval()} [{block.par.Preset.eval()}]" if block.par.Name.eval() else f"{block.index} : {block.par.Preset.eval()}"
			for block 
			in self.ownerComp.op("Cues_RepoMaker").Repo.seq.Cues 
		] )

	@property
	def selected_cue(self):
		return self.ownerComp.par.Selectedcue.menuIndex
		
	@property
	def loop(self):
		return self.ownerComp.par.Loop.eval()

	@property
	def data(self):
		return self.ownerComp.op("Cues_RepoMaker").Repo.seq.Cues
	
	def get_engine(self):
		return self.ownerComp.par.Manager.eval()

	def Reorder(self, sourceIndex:int, targetIndex:int):	
		raise NotImplementedError()

		source_block = self.data[ sourceIndex - 1 ]
		new_block = self.data.insertBlock( targetIndex  )
		new_block.par.Preset.val = source_block.par.Preset.eval()
		new_block.par.Fadetime.val = source_block.par.Fadetime.eval()
		new_block.par.Name.val = source_block.par.Name.eval()
		# self.data.destroyBlock( source_block.index )
		self.ownerComp.op("Cues_RepoMaker").Repo.cook( force = True)

		# 2025 Exclusive :(
		# self.data.moveBlock( sourceIndex, targetIndex)	
		return 


	def Append_Cue(self, preset, time = 5):
		debug("APpending cue")
		self.data.numBlocks += 1
		new_block = self.data[ self.data.numBlocks - 1]
		
		new_block.par.Preset.val = preset
		new_block.par.Fadetime.val = time
		

	def Record_Cue(self, preset, time = 5):
		self.Append_Cue( 
			self.get_engine().Store_Preset( preset ), 
			time=time
		)

	def Delete_Cue(self, index):
		self.data.destroyBlock( index )
	
	def Select_Cue(self, index):
		self.ownerComp.par.Selectedcue.menuIndex = index
		return

	def Select_Next_Cue(self):
		if self.loop: 
			self.Select_Cue( 
				(self.ownerComp.par.Selectedcue.menuIndex + 1) % len( self.ownerComp.par.Selectedcue.menuNames )
			)
		else:
			self.Select_Cue( 
				(self.ownerComp.par.Selectedcue.menuIndex + 1)
			)
	

	def Recall_Cue(self, index, time = None):
		cueData = self.data[ index ]
		
		self.get_engine().Recall_Preset(
			cueData.par.Preset.eval(), 
			time or cueData.par.Fadetime.eval()
		)

		self.ownerComp.par.Activecue.menuIndex = cueData.index
		self.Select_Next_Cue()

		self.ownerComp.op("callbackManager").Do_Callback(
			"onGo",
			index,
			self.selected_cue,
			cueData.par.Preset.eval(),
			self.get_engine().Get_Preset_Name(cueData.par.Preset.eval()),
			cueData.par.Fadetime.eval()
		)


	def Assign_Preset(self, index, preset):
		self.data[index].par.Preset.val = preset

	def Assign_Time(self, index, time):
		self.data[index].par.Fadetime.val = time

	def Go(self):
		self.Recall_Cue(self.selected_cue)
		
		