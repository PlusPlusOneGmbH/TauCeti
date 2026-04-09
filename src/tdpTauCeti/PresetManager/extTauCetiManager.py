'''Info Header Start
Name : extTauCetiManager
Author : wieland@plusplus.one
Saveorigin : TauCeti_PresetSystem.toe
Saveversion : 2025.32460
Info Header End'''

from td import * # pyright: ignore[reportMissingImports]

from typing import Literal, Union
from typing import  TYPE_CHECKING, Any, cast



if TYPE_CHECKING:   
	from tdpTauCeti.Tweener.extTweener import extTweener
	from tdpTauCeti.Tweener.TweenObject import _tween
	from tdpTauCeti.Tweener.curves.extCurve import available_curves
else:
	extTweener = Any
	_tween = Any
	available_curves = Any

def snakeCaseToCamelcase( classObject ):
	import inspect
	from optparse import OptionParser
	for methodName, methodObject in inspect.getmembers(OptionParser, predicate=inspect.isfunction) :
		if methodName[0].isupper():
			setattr( 
				classObject, 
				"".join( word.capitalize() for word in methodName.split("_")),
				methodObject
			)



class PresetDoesNotExist(Exception):
	pass

from asyncio import gather
from dataclasses import dataclass



@dataclass
class PresetRecall:
	name : str
	preset_id : str
	tweens : List[_tween]
	invalid:bool = False

	def __bool__(self):
		return not self.invalid

	@property
	def pars(self):
		return [ tween.parameter for tween in self.tweens ]
	
	@property
	def remaining(self):
		return max(
			[ tween.Remaining for tween in self.tweens]
		)

	@property
	def done(self):
		return all(
			[ tween.Done for tween in self.tweens ]
		)
	
	def pause(self):
		for tween in self.tweens:
			tween.Pause()

	def resume(self):
		for tween in self.tweens:
			tween.Resume()

	def stop(self):
		for tween in self.tweens:
			tween.Stop()

	async def Resolve(self):
		return await gather(*[
			tween.Resolve() for tween in self.tweens
		])
	

TDFunctions = op.TDModules.mod.TDFunctions # pyright: ignore[reportAttributeAccessIssue]

import uuid
from copy import copy
from os import environ
from pathlib import Path


class extTauCetiManager:

	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp 		= ownerComp
		# self.stack     		= self.ownerComp.ext.extParStack # ????
		# self.tweener   		= self.ownerComp.op('olib_dependancy').Get_Component()
		
		self.logger 			= self.ownerComp.op("logger")
		
		try:
			#from tdpTauCeti.Tweener import ToxFile as TweenerToxFile
			#self.tweener	= cast(extTweener, ensure_external(TweenerToxFile, "TAUCETI_TWEENER"))
			from touchutilcollection.ensure import ensure_global_tdp
			from tdpTauCeti import Tweener
			self.Tweener = ensure_global_tdp( Tweener, cast_as=Tweener.Typing )
			self.logger.Log("Importing via TUC")
			
		except ModuleNotFoundError:
			self.Tweener:extTweener = self.ownerComp.op("remote_dependency").GetGlobalComponent()
			# We will use this as a fallback still for folks not using state of the art packagaging technology
			# brought to you in 3D
			self.logger.Log("Imported from RemoteDependency")

		self.preview:TOP 		= self.ownerComp.op("previews")
		
		self.prefab 			= self.ownerComp.op("emptyPreset")
		self.Record_Preset		= self.Store_Preset
		self.PresetDoesNotExist = PresetDoesNotExist
		snakeCaseToCamelcase( self )

	@property
	def _stack(self):
		return self.ownerComp

	@property
	def preset_folder(self):
		return self.ownerComp.op("Presetfolder_RepoMaker").Repo

	def Find_Presets(self, name:str="", tag:str="") -> list[str]:
		"""
			Returns a listpreset_ids of presets given the defined parameters.
		"""
		return_values = []
		for child in self.preset_folder.findChildren(depth = 1):
			if name and child.par.Name.eval() != name: continue
			if tag and child.par.Tag.eval() != name: continue
			return_values.append( child.name )
		return return_values

	def Export_Presets(self, path:str):
		"""
			Save the preset as a TOX for the given path.
		"""
		self.preset_folder.save( path, createFolders = True )

	def Import_Presets(self, path:str):
		"""
			Load a TOX as the external presets.
		"""
		self.preset_folder.par.externaltox = path
		self.preset_folder.par.reinitnet.pulse()
		self.preset_folder.par.externaltox = ""

	def _store_prev(self, prefab):
		prefab.op("preview").par.top = self.ownerComp.op("preview")			
		prefab.op("preview").bypass = False
		prefab.op("preview").lock = False
		prefab.op("preview").bypass = not self.ownerComp.par.Storepreviews.eval()
		prefab.op("preview").lock = self.ownerComp.par.Storepreviews.eval()
		prefab.op("preview").par.top = ""

	def Get_Preset_Comp(self,preset_id) -> COMP :
		"""
			Returns the COMP defining the presets given thepreset_id.
		"""
		return self.preset_folder.op(preset_id) or self.ownerComp.op("emptyPreset")

	def Get_Preset_Name(self,preset_id:str) -> str:
		"""
			Return the Name of a Preset bypreset_id.
		"""
		return self.Get_Preset_Comp(preset_id).par.Name.eval()

	def Get_Preview(self,preset_id:str) -> TOP:
		"""
			Return the TOP showing the preview of the Presets.
		"""

		return self.Get_Preset_Comp(preset_id).opex("preview").asType(TOP)

	def Store_Preset(self, name:str, tag = '',preset_id = "") -> str:
		"""
			Store the Preset unter the given name. 
			Ifpreset_id is not not supplied thepreset_id will be generated based on Parameters.
		"""
		#creating newpreset_id if nopreset_id given.
		if self.ownerComp.par.Idmode.eval() == "Name":
			name = tdu.legalName( name ) # pyright: ignore[reportAttributeAccessIssue]
			preset_id = name
		
		preset_id =preset_id or tdu.legalName( str( uuid.uuid4() ) ) # pyright: ignore[reportAttributeAccessIssue]

		#checking for existing preset
		existing_preset_comp 	= self.preset_folder.op( preset_id ) 

		if existing_preset_comp:
			handle_override = self.ownerComp.par.Handleoverride.eval()
			if handle_override == "Request":
				if not ui.messageBox(
					"Override Preset",
					f"You are about to override the preset with the name {name} andpreset_id {preset_id}. Are you sure?",
					buttons = ["Cancel", "Ok"]
				): return ""
			if handle_override == "Exception":
				raise Exception(f"Preset {preset_id} {name} already exists!")
		
		#calling update or create, depending on if a preset already exists. 
		if existing_preset_comp:
			existing_preset_comp.destroy()

		#preset_comp 		= (self._update_preset if existing_preset else self._create_preset)(name, tag, preset_id)
		# Upadting is for a later time of day. 
		# We should implement the Push here actually!
		preset_comp = self._create_preset( name, tag, preset_id )

		#storing the preview
		self._store_prev( preset_comp )
		
		#aranging the node
		TDFunctions.arrangeNode( preset_comp )

		#writing stack to preset-table
		stack_data =  self.ownerComp.op("callbackManager").Do_Callback("getStack", self.ownerComp) or  self._stack.Get_Stack_Dict_List() 

		preset_comp.seq.Items.numBlocks = len( stack_data )
		data_seq = preset_comp.seq.Items
		for index, item in enumerate( stack_data ):
			if item is None: continue
			item["Operator"] = self.ownerComp.relativePath( item["Operator"]) if self.ownerComp.par.Pathrelation.eval() == "Relative" else item["Operator"].path
			for key, value in item.items():	
				data_seq[index].par[key] = value
			pass

		if self.ownerComp.par.Pushstacktoallpresets.eval():
			self.Push_Stack_To_Presets()
		return preset_id

	@property
	def preset_comps(self):
		return [
			preset_comp for preset_comp in self.preset_folder.findChildren( depth = 1) if hasattr( preset_comp.seq, "Items" )
		]

	def _create_preset(self, name, tag,preset_id):
		new_preset = self.preset_folder.copy( self.prefab, name =preset_id)
		new_preset.par.Tag 	= tag or self.ownerComp.par.Tag.eval()
		new_preset.par.Name = name
		self.ownerComp.op("callbackManager").Do_Callback(	"onPresetRecord", 
															new_preset.par.Name.eval(), 
															new_preset.par.Tag.eval(), 
															new_preset.name,
															self.ownerComp)
		return new_preset

	def _update_preset(self, name, tag,preset_id):
		preset_comp = self.preset_folder.op(id)
		self.ownerComp.op("callbackManager").Do_Callback(	"onPresetUpdate", 
															preset_comp.par.Name.eval(), 
															preset_comp.par.Tag.eval(), 
															preset_comp.name,
															self.ownerComp)
		return preset_comp

	def Remove_Preset(self,preset_id:str ):
		try:
			self.preset_folder.op(preset_id ).destroy()
		except :
			pass
	
	def Remove_All_Presets(self):
		for preset_comp in self.preset_folder.findChildren( depth = 1):
			preset_comp.destroy()

	def Preset_To_Stack(self,preset_id:str):	
		preset_comp = self.preset_folder.op(preset_id )
		if not preset_comp: return
		self._stack.Clear_Stack()

		for block in preset_comp.seq.Items:
			try:
				self._stack.Add_Par( 
					block.par.Parameter.eval(),
					preload = block.par.Preload.eval(),
					fade_type = block.par.Type.eval()
				)

			except AttributeError:
				continue

	def Recall_Preset(self,preset_id:str, time:float, curve:available_curves = "s", load_stack:bool = False):
		
		preset_comp = self.preset_folder.op( preset_id )
		self.logger.Log("Recalling preset", preset_id, time, curve, load_stack)
		
		if not preset_comp: 
			if self.ownerComp.par.Handlenopreset.eval() == "Raise Exception": 
				raise self.PresetDoesNotExist()
			return PresetRecall( "_invalid", preset_id, [], invalid = True)
		
		self.ownerComp.op("callbackManager").Do_Callback(
			"onPresetRecall", 
			preset_comp.par.Name.eval(), 
			preset_comp.par.Tag.eval(), 
			preset_comp.name,
			self.ownerComp
		)

		if load_stack: self.Preset_To_Stack( preset_id )

		tweens = []
		for block in preset_comp.seq.Items:
			
			
			self.ownerComp.par.Evalref.val = block.par.Operator.eval()
			target_operator = self.ownerComp.par.Evalref.eval()
			if target_operator is None: 
				self.logger.Log( "Target operator is None. Skipping.", self.ownerComp.par.Evalref.val )
				continue

			target_parameter = target_operator.par[ block.par.Parname.eval() ]
			
			if target_parameter is None: 
				self.logger.Log(
					"Could not find Parameter stored in Preset", 
					id, 
					block.par.Operator.eval(),
					block.par.Parname.eval()
				)
				continue

			tweens.append(
				self.Tweener.CreateTween(
					target_parameter, 
					block.par.Value.eval(), 
					time, 
					type 	= block.par.Type.eval(), 
					curve 	= curve, 
					id 		= preset_comp, 
					mode 	= block.par.Mode.eval(), 
					expression = block.par.Expression.eval() 
				)
			)

		return PresetRecall(
			preset_comp.par.Name.eval(), 
			preset_id, 
			tweens
		)
	
	def Rename(self,preset_id:str, new_name:str ):
		preset_comp = self.preset_folder.op(preset_id )
		if not preset_comp: return
		
		if self.ownerComp.par.Renamemode.eval() == "Replacepreset_id":
			new_name = tdu.legalName( new_name ) # pyright: ignore[reportAttributeAccessIssue]
			preset_comp.name 			= new_name
			preset_comp.par.Name.val 	= new_name
		else:
			preset_comp.par.Name 		= new_name
		return preset_comp

	def Push_Stack_To_Presets(self, 
						   mode:Literal["keep", "overwrite"] 		= "keep", 
						   _stackelements:Union[str, list, tuple] 	= "*", 
						   _presets:Union[str, list, tuple] 			= "*"):
		"""
			Pushes all the parameters of the current stack to all presets.
			When using "overwrite" mode all parameters will b overwritten. CAUTION!
		"""

		stack_data =  self.ownerComp.op("callbackManager").Do_Callback("getStack", self.ownerComp) or  self._stack.Get_Stack_Dict_List() 
		for preset_comp in self.preset_comps:

			preset_data_seq = preset_comp.seq.Items
			append_data = []
			for stack_item in stack_data :
				
				if stack_item is None: continue
				self.ownerComp.par.Evalref.val = stack_item["Operator"]
				stack_operator = self.ownerComp.par.Evalref.eval()
				if stack_operator is None: continue

				stack_parameter = stack_operator.par[ stack_item["Parname"] ]
				if stack_parameter is None: continue

				for preset_seq_par in preset_data_seq:
					self.ownerComp.par.Evalref.val 	= preset_seq_par.par.Operator.val
					preset_operator					= self.ownerComp.par.Evalref.eval()
					if stack_operator != preset_operator: continue

					preset_parameter = preset_operator.par[ preset_seq_par.par.Parname.eval() ]
					if preset_parameter is None: continue
	

					if hash( preset_parameter ) != hash( stack_parameter ): continue
					if mode == "overwrite": 
						preset_seq_par.par.Value.val = stack_parameter.eval()
					break
				else:
					append_data.append( stack_item )
			

			for _new_value_item in append_data:
				new_value_item = copy( _new_value_item )
				new_block = preset_comp.seq.Items.insertBlock(0)
				if self.ownerComp.par.Pathrelation.eval() == "Relative":
					pass
					new_value_item["Operator"] = self.ownerComp.relativePath( new_value_item["Operator"] )
				else:
					pass
					new_value_item["Operator"] = new_value_item["Operator"].path
				for key, value in new_value_item.items():
					setattr( new_block.par, key, value)
				


		return

	@property
	def PresetParMenuObject(self):
		return tdu.TableMenu(
			self.ownerComp.opex("id_to_name").asType(tableDAT), labelCol = "name"
		)