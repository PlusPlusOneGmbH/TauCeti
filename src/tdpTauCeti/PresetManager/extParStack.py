

'''Info Header Start
Name : extParStack
Author : Wieland PlusPlusOne@AMB-ZEPH15
Saveorigin : TauCeti_PresetSystem.toe
Saveversion : 2023.12000
Info Header End'''



from td import *
if __package__:
	from . import ParUtils
else:
	import ParUtils

from typing import TypedDict, Union, Any, Literal, List, TYPE_CHECKING

class StackElement(TypedDict):
	Type : Literal["fade", "startsnap", "endsnap"]
	Preload : bool
	Value : Union[Any, None]
	Parname : str
	Operator : OP
	Mode : Literal["CONSTANT", "EXPRESSION"]
	Expression : Union[str, None]

	
class InvalidOperator( Exception):
	pass

class extParStack:
	"""
	extParStack description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp


		self.fadeable = ['Float', 'Int', 'XYZ', 'RGB', 'XY', 'RGBA', 'UV', 'UVW']
		self.fade_types = ["fade", "startsnap", "endsnap"]
		self.stack_table = self.ownerComp.op('stack_table')

		self.get_par = self.get_par_dict
		try:
			self.ownerComp.par['x']
		except:
			self.get_par = self.get_par_attr

	@property 
	def relation(self):
		return self.ownerComp.par.Pathrelation.eval()
	
	@property
	def items(self):
		return self.ownerComp.op("Stack_RepoMaker").Repo.seq.Items

	def get_par_attr(self, op_path, par_name):
		return getattr( self.get_op_from_path(op_path).par, par_name)
	
	def get_par_dict(self, op_path, par_name):
		return self.get_op_from_path(op_path).par[par_name]

	def get_path(self, operator):
	
		if self.relation == "Relative":
			return self.ownerComp.op("Stack_RepoMaker").Repo.relativePath( operator )
		return operator.path

	def get_fade_type(self, par):
		if par.style in self.fadeable: return 'fade'
		return  'startsnap'

	def get_op_from_path(self, path):
		self.ownerComp.par.Oppath = path
		targetOperator = self.ownerComp.par.Oppath.eval()#
		if targetOperator is None: raise InvalidOperator(f"Operator {path} does not exist!")
		return targetOperator

	def Get_Parameter(self, op_path, parameter_name):
		return self.get_par( op_path, parameter_name)
		
	def Add_Comp(self, comp, page_scope = "*"):
		custom_page_dict = { page.name : page for page in comp.customPages }
		matched_pages = tdu.match( page_scope, list( custom_page_dict.keys() ) )

		for page_key in matched_pages:
			for parameter in custom_page_dict[ page_key ]:
				self.Add_Par( parameter )

	
	def Add_Par(self, parameter, preload = False, fade_type = ""):
		for item in self.items:
			if item.par.Parameter.eval() == parameter or item.par.Operator.eval() is None: 
				item_block = item
				break
			continue
		else:
			item_block = self.items.insertBlock(0)
		
		item_block.par.Operator.val = self.get_path(parameter.owner)
		item_block.par.Preload.val = preload
		item_block.par.Parname.val = parameter.name
		item_block.par.Type.val = fade_type if fade_type else self.get_fade_type( parameter )
	
	def Get_Stack_Element_Dict(self, index) -> StackElement:
		block = self.items[index]
		parameter = block.par.Parameter.eval()
		if parameter is None: 
			return None
		return {
			"Type" 		: block.par.Type.eval(),
			"Preload" 	: block.par.Preload.eval(),
			"Value" 	: ParUtils.parse( parameter ) if (parameter.mode != ParMode.EXPRESSION) else 0,
			"Parname" 	: block.par.Parname.eval(),
			"Operator"	: block.par.Operator.eval(),
			"Mode"		: parameter.mode.name,
			"Expression": parameter.expr if (parameter.mode == ParMode.EXPRESSION) else None,
		}
	
	def Refresh_Stack(self):
		temp_list = self.Get_Stack_Dict_List()
		self.Clear_Stack()
		for element in temp_list:
			if element["par"]: self.Add_Par( element["par"] )
		return

	def Get_Stack_Dict_List(self) -> List[StackElement]:
		return [ self.Get_Stack_Element_Dict(index) for index in range(0, self.items.numBlocks)]

	def Remove_Row_From_Stack(self, index):
		if self.items.numBlocks > 1:
			self.items.destroyBlock( index )
		else:
			block = self.items[0]
			block.par.Operator.val = ""
			block.par.Parname.val = ""

	def Clear_Stack(self):
		self.items.numBlocks = 1
		for parameter in self.items[0]:
			parameter.reset()
			
			#parameter.val = parameter.default
	
	def Change_Preload(self, index):
		self.items[index].par.Preload.val = not self.items[index].par.Preload.eval() 

	def Change_Fadetype(self, index):
		self.items[index].par.Type.menuIndex = (
			self.items[index].par.Type.menuIndex+1
			) % len( self.items[index].par.Type.menuNames )
		