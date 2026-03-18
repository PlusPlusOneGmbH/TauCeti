



'''Info Header Start
Name : extCuelist
Author : Wieland PlusPlusOne@AMB-ZEPH15
Saveorigin : TauCeti_PresetSystem.toe
Saveversion : 2025.32280
Info Header End'''
class extCuelist:
	"""
	extCuelist description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		self.data = self.ownerComp.op("dictParser")
		#self.cue_table = self.ownerComp.op('cuelist')
		
		# if self.ownerComp.par.Manager.eval() is not None: self.Recall_Cue( "", time = 0 )
	
	@property
	def selected_cue(self):
		return self.ownerComp.par.Selectedcue.eval()
		
	@property
	def loop(self):
		return self.ownerComp.par.Loop.eval()

	def get_engine(self):
		return self.ownerComp.par.Manager.eval()



	def Reorder(self, source_row_index:int, target_slot_index:int):

		next_row_index = target_slot_index + 1
		prev_row_index = target_slot_index 

		next_item_data = self.data.GetItem( 
			min( next_row_index , self.data.NumItems ),
			rows = "id"
	    )

		prev_item_data = self.data.GetItem( 
			max(1, prev_row_index  ),
			rows = "id"
		)

		prev_id = float(prev_item_data["id"]) * bool( target_slot_index == 1) # bool(prev_item_data["_tableIndex"] != 1)
		next_id = float(next_item_data["id"]) + 2 * bool(next_item_data["_tableIndex"] == self.data.NumItems)
		debug( next_item_data, prev_item_data, prev_id, next_id)

		new_cue_id = f"{(next_id + prev_id) / 2:.2f}"

		self.data.UpdateItem(source_row_index, {
			**self.data.GetItem(source_row_index),
			"id" : new_cue_id}
		)
		self._sort()
		
		return 

	def _sort(self):
		self.data.SortTable( key = lambda row: float(row[0]))
		self.Select_Next_Cue()

	def Append_Cue(self, preset, time = None):
		self.data.AddItem({
			"id" : math.floor( 
				float(self.data.GetItem(-1)["id"])
			) + 1 if self.data.NumItems else "1",
			"comment" : "",
			"preset" : preset,
			"time" : self.ownerComp.par.Defaulttime.eval() if time is None else time
		})
		self._sort()


	def Record_Cue(self, preset, time = None):
		self.Append_Cue( 
			self.get_engine().Store_Preset( preset ), 
			time = self.ownerComp.par.Defaulttime.eval() if time is None else time
		)

	def Delete_Cue(self, cue_id):
		self.data.DeleteItem( cue_id )
		self.Select_Next_Cue()
	
	def Select_Cue(self, cue_id):
		self.ownerComp.par.Selectedcue.val = cue_id
		return

	def Select_Next_Cue(self):
		if not self.data.NumItems: return
		next_cue_index = self.ownerComp.par.Activecue.menuIndex + 1
		if self.loop: next_cue_index %= len( self.ownerComp.par.Selectedcue.menuNames )
		else: next_cue_index = tdu.clamp( next_cue_index, 0, len( self.ownerComp.par.Selectedcue.menuNames )-1)
		self.Select_Cue( 
			self.ownerComp.par.Selectedcue.menuNames[ next_cue_index ]
		)
	

	def Recall_Cue(self, cue_id, time = None):
		cueData = self.data.GetItem( cue_id )
		
		self.get_engine().Recall_Preset(cueData["preset"], time or cueData["time"])

		self.ownerComp.par.Activecue.val = cueData["id"]
		self.Select_Next_Cue()

		self.ownerComp.op("callbackManager").Do_Callback(
			"onGo",
			cue_id,
			self.selected_cue,
			cueData["preset"],
			self.get_engine().Get_Preset_Name(cueData["preset"]),
			cueData["time"]
		)
	
		eventcue_id = self.ownerComp.op("event1").createEvent(
			attackTime = cueData["time"]
		)
		self.ownerComp.op("recalled_cues").appendRow(
			[eventcue_id, cue_id]
		)

	def _finalize_cue(self, event_id):
		cue_id = self.ownerComp.op("recalled_cues")[str(event_id), "cueId"].val
		cueData = self.data.GetItem(cue_id)
		presetcue_id = cueData["preset"]
		presetName = self.get_engine().Get_Preset_Name(presetcue_id)

		self.ownerComp.op("callbackManager").Do_Callback(
			"onDone",
			cue_id,
			presetcue_id,
			presetName
		)
		self.ownerComp.op("recalled_cues").deleteRow( str( event_id) )

	def Update_Cue(self, cue_id, dataset:dict):
		self.data.UpdateItem(cue_id, {
			**self.data.GetItem(cue_id),
			**dataset }
		)

	def Assign_Preset(self, cue_id, preset):
		self.Update_Cue(cue_id, {"preset" : preset})

	def Assign_Time(self, cue_id, time):
		self.Update_Cue(cue_id, {"time" : time})

	def Assign_Comment(self, cue_id, comment):
		self.Update_Cue(cue_id, {"comment" : comment })

	def Assign_cue_id(self, cue_id, newcue_id):
		self.Update_Cue(cue_id, {"cue_id" : newcue_id})
		self.data.SortTable( key = lambda row: float(row[0]))
		self.Select_Next_Cue()

	def Go(self):
		self.Recall_Cue(self.selected_cue)
		
		