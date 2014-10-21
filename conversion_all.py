# -------------------------------------------------------------------------------
# Name: conversion_mllw.py
# Purpose: converts points from MLLW to NAVD88 based on a MLLW tidal datum surface
# Author: Andy Bell (ambell@ucdavis.edu)
# Created: 8/27/2014
#-------------------------------------------------------------------------------

import arcpy
from arcpy import env
import exceptions, sys, traceback


#check fieldnames for reserved names: "MSL_m" "Tidal_range_m" "NADV88m"
def check_fieldnames(fc):
	fieldList = arcpy.ListFields(fc)
	reserved = ['MSL_m', 'Tidal_Range_m', 'NAVD88_m', 'Z', 'Z_MEAN', 'WS_MLLW_m', 'Tidal_Datum_Source']
	check = True
	for field in fieldList:
		if field.name in reserved:
			check = False
	return check


# Checks if a fieldname exisits in a featureclass
def fieldExists(inFeatureClass, inFieldName):
	fieldList = arcpy.ListFields(inFeatureClass)
	for iField in fieldList:
		if iField.name.lower() == inFieldName.lower():
			return True
	return False


##### add -> copy -> delete field for arcgis versions <10.2.1 (alter_field does not exist)
def change_fieldname(feature, oldfield, newfield):
	arcpy.AddField_management(feature, newfield, "DOUBLE")
	arcpy.CalculateField_management(feature, newfield, '!' + oldfield + '!', "PYTHON_9.3", "#")
	arcpy.DeleteField_management(feature, oldfield)


try:
	arcpy.CheckOutExtension("3D")
	# Set Local Variables
	inString = arcpy.GetParameterAsText(0)
	mllw_surface = arcpy.GetParameterAsText(1)
	mhw_surface = arcpy.GetParameterAsText(2)  # add parameter to python tbx

	# get list of features
	fcList = inString.split(";")  #splits input string into a list of features

	#arcpy.AddMessage(fcList)

	# interate over feature list and change field names
	# use extract values to points instead of addsurfaceinformation_3d
	for feature in fcList:
		if check_fieldnames(feature) == True:
			arcpy.AddMessage(feature)  #adds feature name to output
			desc = arcpy.Describe(feature)  #feature type
			fc_type = desc.shapeType
			arcpy.AddMessage("Adding field from surface value")

			#todo: insert if/esif statement to check if the feature has field with MLLW or MHW
			if fieldExists(feature,"MLLW_m") == True:
				#Add surface information by input type
				if fc_type == 'Point':
					arcpy.AddSurfaceInformation_3d(feature, mllw_surface, "Z", "LINEAR")
				elif fc_type == 'Polyline':
					arcpy.AddSurfaceInformation_3d(feature, mllw_surface, "Z_MEAN", "LINEAR")
					try:
						arcpy.AlterField_management(feature, "Z_MEAN", "Z", "Z")  # change field name to "Z"
					except:
						change_fieldname(feature, "Z_MEAN", "Z")
				else:
					arcpy.AddError("Issue: Feature type not supported. Only convert lines or points!")

				#change surface info field name
				try:  #attempts to change field using alter_field (arcgis v10.2.1+)
					arcpy.AlterField_management(feature, "Z", "WS_MLLW_m", "WS_MLLW_m")  # changes field name
				except:  #if alterfield does not work. Slower then alter field method for compatibility
					change_fieldname(feature, "Z", "WS_MLLW_m")

				#Add field with raster name for conversion surface

				arcpy.AddField_management(feature, "Tidal_Datum_Source", "TEXT")
				arcpy.CalculateField_management(feature, "Tidal_Datum_Source", '"' + mllw_surface + '"', "PYTHON_9.3")

				#add field to calculate NAVD88 from sounding and mllw_m
				arcpy.AddField_management(feature, "NAVD88_m", "DOUBLE")
				arcpy.CalculateField_management(feature, "NAVD88_m", "!WS_MLLW_M! + !MLLW_m!", "PYTHON_9.3")  #check!!
				arcpy.AddMessage("Calculating NAVD88 Elevation: subtracting MLLW bed elevation from MLLW water surface")

			elif fieldExists(feature, "MHW_m") == True:
				#todo: port over code from the conversion mhw to NAVD88 tool script as a elif statement block.
				#There has got to be a better way to do this since the add/alter field is repetitive
				# but it probably would require restructuring

				if fc_type == 'Point':
					arcpy.AddSurfaceInformation_3d(feature, mhw_surface, "Z", "LINEAR")
				elif fc_type == 'Polyline':
					arcpy.AddSurfaceInformation_3d(feature, mhw_surface, "Z_MEAN", "LINEAR")
					try:
						arcpy.AlterField_management(feature, "Z_MEAN", "Z", "Z")  # change field name to "Z"
					except:
						change_fieldname(feature, "Z_MEAN", "Z")
				else:
					arcpy.AddError("Issue: Feature type not supported. Only convert lines or points!")

				#change surface info field name
				try:  #attempts to change field using alter_field (arcgis v10.2.1+)
					arcpy.AlterField_management(feature, "Z", "WS_MHW_m", "WS_MHW_m")  # changes field name
				except:  #if alterfield does not work. Slower then alter field method for compatibility
					change_fieldname(feature, "Z", "WS_MHW_m")

				#Add field with raster name for conversion surface

				arcpy.AddField_management(feature, "Tidal_Datum_Source", "TEXT")
				arcpy.CalculateField_management(feature, "Tidal_Datum_Source", '"' + mhw_surface + '"', "PYTHON_9.3")

				#add field to calculate NAVD88 from sounding and mhw_m
				arcpy.AddField_management(feature, "NAVD88_m", "DOUBLE")
				arcpy.CalculateField_management(feature, "NAVD88_m", "!WS_MHW_m! + !MHW_m!", "PYTHON_9.3")  #check!!
				arcpy.AddMessage("Calculating NAVD88 Elevation")

		else:
			arcpy.AddError("Issue: fields already exist for feature. Delete problem fields and try again")
			break


except arcpy.ExecuteError:
	print arcpy.GetMessages()