import arcpy


class Toolbox(object):
	def __init__(self):
		"""Define the toolbox (the name of the toolbox is the name of the
		.pyt file)."""
		self.label = "HistoricalDEM"
		self.alias = "Historical DEM Toolbox"

		# List of tool classes associated with this toolbox
		self.tools = [Tool, DeleteConversionFields]


class Tool(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Tool"
		self.description = ""
		self.canRunInBackground = False

	def getParameterInfo(self):
		"""Define parameter definitions"""
		params = None
		return params

	def isLicensed(self):
		"""Set whether tool is licensed to execute."""
		return True

	def updateParameters(self, parameters):
		"""Modify the values and properties of parameters before internal
		validation is performed.  This method is called whenever a parameter
		has been changed."""
		return

	def updateMessages(self, parameters):
		"""Modify the messages created by internal validation for each tool
		parameter.  This method is called after internal validation."""
		return

	def execute(self, parameters, messages):
		"""The source code of the tool."""
		return


class DeleteConversionFields(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "DeleteConversionFields"
		self.description = "Delete Conversion fields from all the features. Uses a reserved " \
						   "list ['MSL_m', 'Tidal_Range_m', 'NAVD88_m', 'WS_MLLW_m', 'Tidal_Datum_Source'"
		self.canRunInBackground = False

	def getParameterInfo(self):
		"""Define parameter definitions"""
		fcList = arcpy.Parameter(displayName="Input Features", name="fcList", datatype="DEFeatureClass",
								 parameterType="Required",multiValue=True)

		#reserved = ['MSL_m', 'Tidal_Range_m', 'NAVD88_m', 'WS_MLLW_m', 'Tidal_Datum_Source', 'WS_MHW_m']
		fields = arcpy.Parameter(displayName="Fields to Delete", name="fields", datatype="GPString",
								 parameterType="Optional", multiValue=True)
		fields.filter.type = "ValueList"
		fields.filter.list = ['MSL_m', 'Tidal_Range_m', 'NAVD88_m', 'WS_MLLW_m', 'Tidal_Datum_Source', 'WS_MHW_m']


		parameters = [fcList, fields]
		return parameters


	def updateParameters(self, parameters):
		"""Modify the values and properties of parameters before internal
		validation is performed.  This method is called whenever a parameter
		has been changed."""
		return

	def updateMessages(self, parameters):
		"""Modify the messages created by internal validation for each tool
		parameter.  This method is called after internal validation."""
		return

	def execute(self, parameters, messages):
		"""The source code of the tool."""
		inString = arcpy.GetParameterAsText(0)
		fcList = inString.split(";")
		# interate over feature list and change field names
		for feature in fcList:
			arcpy.AddMessage(feature) #adds feature name to output


		field_parameter = arcpy.GetParameterAsText(1)
		arcpy.AddMessage(field_parameter)
		fields = field_parameter.split(';')
		# interate over feature list and change field names
		for field in fields:
			arcpy.AddMessage("name: %s" %field) #adds feature name to output
		return
