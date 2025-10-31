'''Info Header Start
Name : extPresetMapper
Author : Wieland PlusPlusOne@AMB-ZEPH15
Saveorigin : TauCeti_PresetSystem.toe
Saveversion : 2023.12000
Info Header End'''
class extPresetMapper:
	"""
	extPresetMapper description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		#self.maps = self.ownerComp.op('maps')
		self.learn_table = self.ownerComp.op('learn')
		self.selector = self.ownerComp.op('selector')

		self.selected_index = 0

	@property
	def maps(self):
		return self.ownerComp.op("repo_maker").Repo
	
	def get_engine(self):
		return self.ownerComp.par.Manager.eval()

	def Do_Map(self, name, time):
		for preset in self.maps.rows( name ):
			self.get_engine().Recall_Preset( preset[1].val, time)

	def Set_Name(self, index, name):
		self.maps[index, 'name'] = name

	def Open_Selection(self, index):
		self.selected_index = index
		self.selector.par.display = True
		return

	def Clear_Preset(self, index):
		self.maps[ index, "preset"] = ''

	def Select_Preset(self, value):
		self.selector.par.display = False
		if not value: return
		self.maps[ self.selected_index, "preset"] = value
		
	def Learn(self, index):
		learn_cell = self.learn_table[str(index), 0]
		if learn_cell is None:
			return self.learn_table.appendRow( index )
		self.learn_table.deleteRow( learn_cell.row )

	def Handle_On(self, name, time):
		for index in self.learn_table.rows():
			self.maps[ int( index[0].val ), "name"] = name
		self.learn_table.clear()

		self.Do_Map( name, time )
		return