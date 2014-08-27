#-------------------------------------------------------------------------------
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
	reserved = ['MSL_m', 'Tidal_Range_m', 'NAVD88_m', 'Z', 'Z_MEAN', 'WS_MLLW_m']
	for field in fieldList:
		if field.name in reserved:
			return False
		else:
			return True


##### add -> copy -> delete field for arcgis versions <10.2.1 (alter_field does not exist)
def change_fieldname(feature, oldfield, newfield):
	arcpy.AddField_management(feature, newfield, "DOUBLE")
	arcpy.CalculateField_management (feature, newfield, '!' + oldfield + '!', "PYTHON_9.3", "#")
	arcpy.DeleteField_management(feature, oldfield)


try:
	arcpy.CheckOutExtension("3D")
	# Set Local Variables
	inString = arcpy.GetParameterAsText(0)
	mllw_surface = arcpy.GetParameterAsText(1)

	# get list of features
	fcList = inString.split(";") #splits input string into a list of features

	arcpy.AddMessage(fcList)

	# interate over feature list and change field names
	# use extract values to points instead of addsurfaceinformation_3d
	for feature in fcList:
		arcpy.AddMessage(feature) #adds feature name to output
		desc = arcpy.Describe(feature) #feature type
		fc_type = desc.shapeType
		arcpy.AddMessage("Adding Mean Lower Low Water Field for water surface")
		
		#Add surface information by input type
		if fc_type == 'Point':
			arcpy.AddSurfaceInformation_3d(feature, mllw_surface, "Z", "LINEAR")
		elif fc_type == 'Polyline':
			arcpy.AddSurfaceInformation_3d(feature, mllw_surface, "Z_MEAN", "LINEAR")
			try:
				arcpy.AlterField_management(feature, "Z_MEAN", "Z", "Z") # change field name to "Z"
			except:
				change_fieldname(feature, "Z_MEAN", "Z")
		else:
			arcpy.AddError("Issue: Feature type not supported. Only convert lines or points!")
		
		#change surface info field name
		try: #attempts to change field using alter_field (arcgis v10.2.1+)
			arcpy.AlterField_management(feature, "Z", "WS_MLLW_m", "WS_MLLW_m") # changes field name
		except: #if alterfield does not work. Slower then alter field method for compatibility
			change_fieldname(feature, "Z", "WS_MLLW_m")
		#add field to calculate NAVD88 from sounding and mllw_m
		arcpy.AddField_management(feature, "NAVD88_m", "DOUBLE")
		arcpy.CalculateField_management(feature, "NAVD88_m", "!WS_MLLW_M! + !MLLW_m!", "PYTHON_9.3") #check!!
		arcpy.AddMessage("Calculating NAVD88 Elevation: subtracting MLLW bed elevation from MLLW water surface")


except arcpy.ExecuteError:
	print arcpy.GetMessages()


"""#checks if feature contains reserved field names
        if check_fieldnames(feature) == False:
            arcpy.AddError("Issue: fields already exist for feature. Delete problem fields and try again")"""