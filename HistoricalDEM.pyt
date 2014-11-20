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
		param1 = parameters[0].value.exportToString()
		fcList = param1.split(";")  # list of features to modify by removing fields

		param2 = parameters[1].value.exportToString()
		fields_to_remove = param2.split(';')  # the fields that the user selected to delete from the features

		# interate over feature list and deletes all of the field that are were selected
		for feature in fcList:
			arcpy.AddMessage(feature)  # adds feature name to output
			fieldList = arcpy.ListFields(feature)  # list of all fields in each feature
			for field in fieldList:
				if field.name in fields_to_remove:  # if field name matches a name in reserved list
					arcpy.AddMessage("Deleting Reserved Fieldname: %s" %(field.name))
					arcpy.DeleteField_management(feature, field.name)  # field is deleted

		return
