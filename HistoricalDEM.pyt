# ---------------------------------------------------------------------------------------------------
# Name: HistoricalDEM.pyt
# Purpose: ArcGIS python toolbox containing geoprocessing tools for the Delta Historical DEM project
# Author: Andy Bell (ambell@ucdavis.edu)
# Created: 11/20/2014
# ---------------------------------------------------------------------------------------------------

import arcpy
import os
import glob
import make_zip  # imports make_zip.py as module
import shutil



class Toolbox(object):
	def __init__(self):
		"""Define the toolbox (the name of the toolbox is the name of the
		.pyt file)."""
		self.label = "HistoricalDEM"
		self.alias = "Historical DEM Toolbox"

		# List of tool classes associated with this toolbox
		self.tools = [DeleteConversionFields, TidalDatumConversion, TIN_Display, TIN2ASCII]


class DeleteConversionFields(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "DeleteConversionFields"
		self.description = "Delete Conversion fields from all the features. Uses a reserved " \
						   "list ['Tidal_Range_m', 'NAVD88_m', 'WS_MLLW_m', 'Tidal_Datum_Source'"
		self.canRunInBackground = False

	def getParameterInfo(self):
		"""Define parameter definitions"""
		fcList = arcpy.Parameter(displayName="Input Features", name="fcList", datatype="GPFeatureLayer",
								 parameterType="Required", multiValue=True)

		fields = arcpy.Parameter(displayName="Fields to Delete", name="fields", datatype="GPString",
								 parameterType="Optional", multiValue=True)
		fields.filter.type = "ValueList"
		fields.filter.list = ['Tidal_Range_m', 'NAVD88_m', 'WS_MLLW_m', 'Tidal_Datum_Source', 'WS_MHW_m']

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

		# iterate over feature list and deletes all of the field that are were selected
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

		inputs = arcpy.Parameter(displayName="Input Features", name="inputs", datatype="GPFeatureLayer",
								 parameterType="Required", multiValue=True)

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
			checked_versions = ['10.2.1', '10.2.2', '10.3']
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

		# add message if a feature class has a field in the reserved list of fieldnames
		# check fieldnames for reserved names
		def check_fieldnames(fc):
			fieldList = arcpy.ListFields(fc)
			reserved = ['Tidal_Range_m', 'NAVD88_m', 'Z', 'Z_MEAN', 'WS_MLLW_m', 'Tidal_Datum_Source']
			check = True
			for field in fieldList:
				if field.name in reserved:
					check = False
			return check

		if parameters[0].value:
			fcs = parameters[0].value.exportToString()
			fcList = fcs.split(";")  # list of features to modify

			for feature in fcList:
				if check_fieldnames(feature) is False:
					parameters[0].setErrorMessage("Reserved fields already exist for %s. Please use "
					                              "DeleteConversionFields tool first" %feature)
		return

	def execute(self, parameters):
		"""The source code of the tool."""
		param1 = parameters[0].value.exportToString()
		fcList = param1.split(";")  # list of features to modify
		mllw_surface = parameters[1].valueAsText.replace('\\', '\\\\')
		mhw_surface = parameters[2].valueAsText.replace('\\', '\\\\')

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

			# MLLW calculations
			if fieldExists(feature, "MLLW_m"):
				# Add surface information by input type. Anything except points/lines will error.
				if fc_type == 'Point':
					arcpy.AddSurfaceInformation_3d(feature, mllw_surface, "Z", "LINEAR")
					arcpy.AlterField_management(feature, "Z", "WS_MLLW_m", "WS_MLLW_m")  # changes field name to WS_mllw_m
				elif fc_type == 'Polyline':
					arcpy.AddSurfaceInformation_3d(feature, mllw_surface, "Z_MEAN", "LINEAR")
					arcpy.AlterField_management(feature, "Z_MEAN", "WS_MLLW_m", "WS_MLLW_m")  # changes field name to WS_mllw_m
				else:
					arcpy.AddError("Issue: Feature type not supported. Only convert lines or points!")

				arcpy.AddMessage("Calculating NAVD88 Elevation: subtracting MLLW bed elevation from MLLW water surface")

				# Add field with raster name for documenting source of conversion surface
				arcpy.AddField_management(feature, "Tidal_Datum_Source", "TEXT")
				arcpy.CalculateField_management(feature, "Tidal_Datum_Source", '"' + mllw_surface + '"', "PYTHON_9.3")

				# add field to calculate NAVD88 from sounding/line value and mllw_m
				arcpy.AddField_management(feature, "NAVD88_m", "DOUBLE")
				arcpy.CalculateField_management(feature, "NAVD88_m", "!WS_MLLW_M! + !MLLW_m!", "PYTHON_9.3")

			# MHW calculations
			elif fieldExists(feature, "MHW_m"):
				# TODO is there a better way to do this since the add/alter field is repetitive
				if fc_type == 'Point':
					arcpy.AddSurfaceInformation_3d(feature, mhw_surface, "Z", "LINEAR")
					arcpy.AlterField_management(feature, "Z", "WS_MHW_m", "WS_MHW_m")  # changes z to WS_MHW_m
				elif fc_type == 'Polyline':
					arcpy.AddSurfaceInformation_3d(feature, mhw_surface, "Z_MEAN", "LINEAR")
					arcpy.AlterField_management(feature, "Z_MEAN", "WS_MHW_m", "WS_MHW_m")  # changes Z_mean to WS_MHW_m
				else:
					arcpy.AddError("Issue: Feature type not supported. Only convert lines or points!")

				arcpy.AddMessage("Calculating NAVD88 Elevation: adding value from MHW surface")

				# Add field with raster name for conversion surface
				arcpy.AddField_management(feature, "Tidal_Datum_Source", "TEXT")
				arcpy.CalculateField_management(feature, "Tidal_Datum_Source", '"' + mhw_surface + '"', "PYTHON_9.3")

				# add field to calculate NAVD88 from sounding and mhw_m
				arcpy.AddField_management(feature, "NAVD88_m", "DOUBLE")
				arcpy.CalculateField_management(feature, "NAVD88_m", "!WS_MHW_m! + !MHW_m!", "PYTHON_9.3")
		return


class TIN_Display(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "TIN_Display"
		self.description = "Create a TIN from all the layers in a group for the current map extent"
		self.canRunInBackground = False

	def getParameterInfo(self):
		"""Define parameter definitions"""
		tin_output = arcpy.Parameter(displayName="TIN Output", name="tin", datatype="DETin",
								 parameterType="Required", direction="Output")

		# default symbology for the tin output parameter
		tin_output.symbology = os.path.join(os.path.dirname(__file__), 'TIN_symbology_2.lyr')

		tin_group = arcpy.Parameter(displayName="TIN Group", name="tin_group", datatype="GPGroupLayer",
		                            parameterType="Required", direction="Input")

		height_field = arcpy.Parameter(displayName="Elevation Field (z)", name="height_field", datatype="GPString",
		                               parameterType="Required")

		hard_clip = arcpy.Parameter(displayName="Boundary", name="hard_clip", datatype="GPFeatureLayer",
		                            parameterType="Optional")

		hard_clip.filter.list = ["Polygon"]

		# TODO: add projection parameter????

		parameters = [tin_group, height_field, tin_output, hard_clip]
		return parameters

	def isLicensed(self):
		"""Set whether tool is licensed to execute."""

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

		z_filter = parameters[1].filter
		z_filter.list = ["NAVD88_m", "MLLW_m", "Z"]

		return

	def updateMessages(self, parameters):
		"""Modify the messages created by internal validation for each tool
		parameter.  This method is called after internal validation."""

		# TODO: run check that parameter value for height exists for each feature in the group
		# TODO: run check that features in group only contain Points or Polylines
		return

	def execute(self, parameters, messages):
		"""The source code of the tool."""
		tin_in_group = parameters[0].valueAsText
		z_field = parameters[1].valueAsText
		output = parameters[2].valueAsText
		hard_clip = parameters[3].valueAsText
		arcpy.AddMessage("Hard clip: %s" % hard_clip)

		base = os.path.basename(output)
		arcpy.AddMessage(base)

		# projection info
		proj = "PROJCS['NAD_1983_UTM_Zone_10N',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-123.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]"

		# Get display extent from layout view (not sure if there is a better way since data view extent
		# depends on the size of arcmap window)
		imxd = arcpy.mapping.MapDocument("Current")  # set current mxd
		df = arcpy.mapping.ListDataFrames(imxd)[0]  # set first dataframe in current map document
		arcpy.env.extent = df.extent  # set's the env extent to match the display extent

		# Data dictionary to store tin inputs and feature type
		tinputs = {}

		for layer in arcpy.mapping.ListLayers(imxd):  # needed to figure out TOC groups
			if layer.name == tin_in_group:  # TOC layer/group that matches the tin group parameter
				arcpy.AddMessage("TIN inputs: ")
				for subLayer in layer:
					arcpy.AddMessage(subLayer)
					if arcpy.Describe(subLayer).shapeType == "Point":
						tinputs[subLayer.name] = "Mass_Points"
					elif arcpy.Describe(subLayer).shapeType == "Polyline":
						tinputs[subLayer.name] = "Hard_Line"
		# build Tin input format ("Group_Name/file_name z_field Type <None>;")
		Tin_input_strings = []

		for feature in tinputs:
			feature_str = tin_in_group + "/" + feature + " " + z_field + " " + tinputs[feature] + " " + "<None>"
			Tin_input_strings.append(feature_str)

		# if there is a value for hard clip, then append the feature to the tin input string
		if hard_clip is not None:
			Tin_input_strings.append(hard_clip + " " + "<None>" + " " + "Hard_Clip" + " " + "<None>")

		# joins all strings together (semicolon separated)
		Tin_input_str = ";".join(Tin_input_strings) # joins all individual strings together separated by semicolon

		# Create TIN
		arcpy.CreateTin_3d(output, proj, Tin_input_str, "DELAUNAY")
		return


class TIN2ASCII(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "TIN2ASCII"
		self.description = "Converts a TIN to a bunch of ASCII files and zips them up"

	def getParameterInfo(self):
		"""Define parameter definitions"""
		tin = arcpy.Parameter(displayName="TIN", name="tin", datatype="DETin",
								 parameterType="Required", direction="Input")

		output_folder = arcpy.Parameter(displayName="Output Folder", name="output_folder",
		                               datatype="DEFolder", parameterType="Required", direction="Input")

		zip_ascii = arcpy.Parameter(displayName="Zip Files?", name="zip_ascii",
		                            datatype="GPBoolean", parameterType="Optional")

		rm_files = arcpy.Parameter(displayName="Interim files to Remove?", name="rm_files", datatype="GPString",
		                           parameterType="Optional", multiValue=True)

		rm_files.filter.type = "ValueList"
		rm_files.filter.list = ['Raster', 'Raster_Tiles', 'ASCII_Tiles']

		params = [tin, output_folder, zip_ascii, rm_files]
		return params

	def isLicensed(self):
		"""Set whether tool is licensed to execute."""
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
		return

	def execute(self, parameters, messages):
		"""The source code of the tool."""
		# Parameters
		tin = parameters[0].valueAsText
		output_folder = parameters[1].valueAsText
		zip_ascii = parameters[2].valueAsText
		rm_string = parameters[3].value.exportToString()
		rm_list = rm_string.split(';')  # the file types that the user selected to delete

		# Raster size settings
		sampling = "CELLSIZE 2"
		ntiles = "5 5"  # tile dimensions

		# Calculation of total number of tiles desired
		spl = ntiles.split()
		total_tiles = int(float(spl[0])) * int(float(spl[1]))

		# Create folder for output folder
		arcpy.AddMessage("Creating an export folder in %s" % output_folder)
		try:
			os.makedirs(output_folder + "\\raster_tiles")
			r_tiles = os.path.join(output_folder, "raster_tiles")
			os.makedirs(output_folder + "\\ascii_tiles")
			a_tiles = os.path.join(output_folder, "ascii_tiles")
		except Exception as e:
			arcpy.AddError("Can't make folders..... try saving in a different location.")
			arcpy.AddError(e)

		try:
			# Get TIN basename
			base = os.path.basename(tin)
			arcpy.AddMessage("Saving %s as Raster......" % base)
			TinAsRast = os.path.join(output_folder, base + '.TIF')

			# TIN to raster
			arcpy.TinRaster_3d(tin, TinAsRast, 'FLOAT', 'LINEAR', sampling)
		except Exception as e:
			arcpy.AddError("Unable to convert TIN to .TiF")
			arcpy.AddError(e)

		try:
			# Split raster into chunks
			arcpy.AddMessage("Breaking %s into %s raster tiles...." % (base, total_tiles))
			arcpy.SplitRaster_management(TinAsRast, r_tiles, base + '_', 'NUMBER_OF_TILES', 'TIFF', 'BILINEAR', ntiles,
			                             '#', '10', 'METERS')

			# Get list of split tiles
			rastertiles_list = glob.glob(r_tiles + '/*.TIF')

			for raster in rastertiles_list:
				arcpy.AddMessage("Converting %s to ASCII....." % raster)
				rbase = os.path.basename(raster)
				rbaseName, rbaseExt = os.path.splitext(rbase)
				ascii_name = os.path.join(a_tiles, rbaseName + '.txt')
				arcpy.RasterToASCII_conversion(raster, ascii_name)
		except Exception as e:
			arcpy.AddError("Unable to split raster into tiles.")
			arcpy.AddError(e)

		try:
			# zips files using make_zip.py
			if zip_ascii == 'true':
				arcpy.AddMessage("Zipping ASCII files...")
				zipped_output = os.path.join(output_folder, base + "_ascii_tiles.zip")
				make_zip.zip_folder(a_tiles, zipped_output)
				arcpy.AddMessage("All zipped up....")

			# add code to remove temporary files if selected
			arcpy.AddMessage("Removing Interim Files.....")
			if 'Raster' in rm_list:
				arcpy.AddMessage("Deleting full raster")
				arcpy.Delete_management(TinAsRast)  # unable to use os.remove since arc has .tif open
			if 'Raster_Tiles' in rm_list:
				arcpy.AddMessage("Deleting raster tiles")
				shutil.rmtree(r_tiles)
			if "ASCII_Tiles" in rm_list:
				arcpy.AddMessage("Deleting ASCII tiles")
				shutil.rmtree(a_tiles)

		except Exception as e:
			# print e.message
			arcpy.AddError("Unable to zip or delete files")
			arcpy.AddError(e)

		arcpy.GetMessages()
		return
