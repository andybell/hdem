import arcpy


class Toolbox(object):
	def __init__(self):
		"""Define the toolbox (the name of the toolbox is the name of the
		.pyt file)."""
		self.label = "HistoricalDEM"
		self.alias = "Historical DEM Toolbox"

		# List of tool classes associated with this toolbox
		self.tools = [Tool, DeleteConversionFields, TidalDatumConversion]


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


class TidalDatumConversion(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "TidalDatumConversion"
		self.description = "Converts feature elevation to NAVD88 using a raster surface of MLLW and MHW. Each input " \
		                   "needs to have a field named either 'MLLW_m' or 'MHW_m'. The tool will add the appropriate " \
		                   "values to the attribute table including the elevation in NAVD88"
		self.canRunInBackground = False

	def getParameterInfo(self):
		"""Define parameter definitions"""

		inputs = arcpy.Parameter(displayName="Input Features", name="inputs", datatype="DEFeatureClass",
								 parameterType="Required",multiValue=True)

		mllw_surface = arcpy.Parameter(displayName="MLLW Surface Raster", name="mllw_surface",
		                               datatype="GPRasterLayer", parameterType="Required")

		mhw_surface = arcpy.Parameter(displayName="MHW Surface Raster", name="mhw_surface",
		                               datatype="GPRasterLayer", parameterType="Required")

		params = [inputs, mllw_surface, mhw_surface]
		return params

	def isLicensed(self):
		"""Set whether tool is licensed to execute."""
		"""Checks if ArcGIS version > 10.2.1, which is required to run the AlterField_management tool"""
		try:
			info_dict = arcpy.GetInstallInfo()
			version = info_dict['Version']
			checked_versions = ['10.2.1', '10.2.2']
			if version in checked_versions:
				pass
			else:
				raise VersionError
		except VersionError:
			return False

		"""The tool will only execute  if 3D analyst extension is available"""
		try:
			if arcpy.CheckExtension("3D") == "Available":
				arcpy.CheckOutExtension("3D")
			else:
				raise LicenseError

		except LicenseError:
			return False

		return True


	def updateParameters(self, parameters):
		"""Modify the values and properties of parameters before internal
		validation is performed.  This method is called whenever a parameter
		has been changed."""
		return

	def updateMessages(self, parameters):
		"""Modify the messages created by internal validation for each tool
		parameter.  This method is called after internal validation."""

		#TODO add message if a feature class has a field in the reserved list of fieldnames

		#needs to be something like....
		#check fieldnames for reserved names: "MSL_m" "Tidal_range_m" "NADV88m"
		def check_fieldnames(fc):
			fieldList = arcpy.ListFields(fc)
			reserved = ['MSL_m', 'Tidal_Range_m', 'NAVD88_m', 'Z', 'Z_MEAN', 'WS_MLLW_m', 'Tidal_Datum_Source']
			check = True
			for field in fieldList:
				if field.name in reserved:
					check = False
			return check
		return

	def execute(self, parameters, messages):
		"""The source code of the tool."""

		param1 = parameters[0].value.exportToString()
		fcList = param1.split(";")  # list of features to modify
		mllw_surface = parameters[1].valueAsText
		mhw_surface = parameters[2].valueAsText

		# Checks if a field name exists in a feature class
		def fieldExists(inFeatureClass, inFieldName):
			fieldList = arcpy.ListFields(inFeatureClass)
			for iField in fieldList:
				if iField.name.lower() == inFieldName.lower():
					return True
			return False

		# loop through all features in feature class list and adds fields for either MHW or MLLW calcs
		for feature in fcList:
			arcpy.AddMessage(feature)
			fc_type = arcpy.Describe(feature).shapeType

			#MLLW calculations
			if fieldExists(feature, "MLLW_m"):
				#Add surface information by input type. Anything except points/lines will error.
				if fc_type == 'Point':
					arcpy.AddSurfaceInformation_3d(feature, mllw_surface, "Z", "LINEAR")
					arcpy.AlterField_management(feature, "Z", "WS_MLLW_m", "WS_MLLW_m")  # changes field name to WS_mllw_m
				elif fc_type == 'Polyline':
					arcpy.AddSurfaceInformation_3d(feature, mllw_surface, "Z_MEAN", "LINEAR")
					arcpy.AlterField_management(feature, "Z_MEAN", "WS_MLLW_m", "WS_MLLW_m")  # changes field name to WS_mllw_m
				else:
					arcpy.AddError("Issue: Feature type not supported. Only convert lines or points!")

				#Add field with raster name for documenting source of conversion surface
				arcpy.AddField_management(feature, "Tidal_Datum_Source", "TEXT")
				arcpy.CalculateField_management(feature, "Tidal_Datum_Source", '"' + mllw_surface + '"', "PYTHON_9.3")

				#add field to calculate NAVD88 from sounding/line value and mllw_m
				arcpy.AddField_management(feature, "NAVD88_m", "DOUBLE")
				arcpy.CalculateField_management(feature, "NAVD88_m", "!WS_MLLW_M! + !MLLW_m!", "PYTHON_9.3")
				arcpy.AddMessage("Calculating NAVD88 Elevation: subtracting MLLW bed elevation from MLLW water surface")

			#MHW calculations
			elif fieldExists(feature, "MHW_m"):
				#TODO is there a better way to do this since the add/alter field is repetitive
				if fc_type == 'Point':
					arcpy.AddSurfaceInformation_3d(feature, mhw_surface, "Z", "LINEAR")
					arcpy.AlterField_management(feature, "Z", "WS_MHW_m", "WS_MHW_m")  # changes z to WS_MHW_m
				elif fc_type == 'Polyline':
					arcpy.AddSurfaceInformation_3d(feature, mhw_surface, "Z_MEAN", "LINEAR")
					arcpy.AlterField_management(feature, "Z_MEAN", "WS_MHW_m", "WS_MHW_m")  # changes Z_mean to WS_MHW_m
				else:
					arcpy.AddError("Issue: Feature type not supported. Only convert lines or points!")

				#Add field with raster name for conversion surface
				arcpy.AddField_management(feature, "Tidal_Datum_Source", "TEXT")
				arcpy.CalculateField_management(feature, "Tidal_Datum_Source", '"' + mhw_surface + '"', "PYTHON_9.3")

				#add field to calculate NAVD88 from sounding and mhw_m
				arcpy.AddField_management(feature, "NAVD88_m", "DOUBLE")
				arcpy.CalculateField_management(feature, "NAVD88_m", "!WS_MHW_m! + !MHW_m!", "PYTHON_9.3")
				arcpy.AddMessage("Calculating NAVD88 Elevation: adding value from MHW surface")

		return