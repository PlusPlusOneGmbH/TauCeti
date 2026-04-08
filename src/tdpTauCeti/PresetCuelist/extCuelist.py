'''Info Header Start
Name : extCuelist
Author : wieland@plusplus.one
Saveorigin : TauCeti_PresetSystem.toe
Saveversion : 2025.32460
Info Header End'''


from typing import TypedDict, Union, NotRequired

class Cuelist_Entry(TypedDict):
	id : NotRequired[str]
	comment : NotRequired[str]
	preset : NotRequired[str]
	time : NotRequired[float]

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
		if source_row_index > target_slot_index:
			nextIndex = target_slot_index
			prevIndex = target_slot_index - 1
		else :
			nextIndex = target_slot_index + 1
			prevIndex = target_slot_index

		next_item_data:dict = self.data.GetItem( 
			tdu.clamp( nextIndex ,1, self.data.NumItems ),
			rows = "id"
	    )

		prev_item_data:dict = self.data.GetItem( 
			tdu.clamp( prevIndex ,1, self.data.NumItems ),
			rows = "id"
		)


		if prev_item_data["_tableIndex"] == 1 and next_item_data["_tableIndex"] == 1:
			prev_index = 0
			next_index = float(next_item_data["id"])
		elif prev_item_data["_tableIndex"] == self.data.NumItems and next_item_data["_tableIndex"] == self.data.NumItems:
			prev_index = float(prev_item_data["id"])
			next_index = float(next_item_data["id"]) + 2
		else:
			prev_index = float(prev_item_data["id"])
			next_index = float(next_item_data["id"])

		new_cue_id = f"{(next_index + prev_index) / 2:.2f}"

		self.data.UpdateItem(source_row_index, {
			**self.data.GetItem(source_row_index),
			"id" : new_cue_id}
		)
		self.Sort()
		
		return 

	def Sort(self):
		self.data.SortTable( key = lambda row: float(row[0]))
		self.Select_Next_Cue()

	def Append_Cue(self, preset:str, time:Union[None, float] = None):
		new_id =  math.floor( 
				float(self.data.GetItem(-1)["id"])
			) + 1 if self.data.NumItems else 1.0
		
		self.data.AddItem({
			"id" :f"{new_id:.2f}",
			"comment" : "",
			"preset" : preset,
			"time" : self.ownerComp.par.Defaulttime.eval() if time is None else time
		})
		self.Sort()


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
	

	def Recall_Cue(self, cue_id:str, time = None):
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

	def Update_Cue(self, cue_id:str, dataset:Cuelist_Entry):
		self.data.UpdateItem(cue_id, {
			**self.data.GetItem(cue_id),
			**dataset }
		)

	def Assign_Preset(self, cue_id:str, preset:str):
		self.Update_Cue(cue_id, {"preset" : preset})

	def Assign_Time(self, cue_id:str, time):
		self.Update_Cue(cue_id, {"time" : time})

	def Assign_Comment(self, cue_id:str, comment:str):
		self.Update_Cue(cue_id, {"comment" : comment })

	def Assign_cue_id(self, cue_id:str, newcue_id:str):
		self.Update_Cue(cue_id, {"id" : newcue_id})
		self.Sort()

	def Go(self):
		self.Recall_Cue(self.selected_cue)
		
		