#-------------------------------------------------------------------------------
# Name: conversion_mhw_.py
# Purpose: converts points from mhw elevations to NAVD88 based on a mhw tidal datum surface
# Author: Andy Bell (ambell@ucdavis.edu)
# Created: 10/15/2014
#-------------------------------------------------------------------------------

import arcpy
from arcpy import env
import exceptions, sys, traceback

# TODO: move section of the code over to convertion_mllw so everything is able to run through one tool interface
# TODO: then this script/tool can be deleted


#check fieldnames for reserved names
def check_fieldnames(fc):
	fieldList = arcpy.ListFields(fc)
	reserved = ['MSL_m', 'Tidal_Range_m', 'NAVD88_m', 'Z', 'Z_MEAN', 'WS_MHW_m', 'Tidal_Datum_Source']
	check = True
	for field in fieldList:
		if field.name in reserved:
			check = False
	return check

##### add -> copy -> delete field for arcgis versions <10.2.1 (alter_field does not exist)
def change_fieldname(feature, oldfield, newfield):
	arcpy.AddField_management(feature, newfield, "DOUBLE")
	arcpy.CalculateField_management (feature, newfield, '!' + oldfield + '!', "PYTHON_9.3", "#")
	arcpy.DeleteField_management(feature, oldfield)


try:
	arcpy.CheckOutExtension("3D")
	# Set Local Variables
	inString = arcpy.GetParameterAsText(0)
	mhw_surface = arcpy.GetParameterAsText(1)
	
	# get list of features
	fcList = inString.split(";") #splits input string into a list of features

	#arcpy.AddMessage(fcList)

	# interate over feature list and change field names
	# use extract values to points instead of addsurfaceinformation_3d
	for feature in fcList:
		if check_fieldnames(feature) == True:
			arcpy.AddMessage(feature) #adds feature name to output
			desc = arcpy.Describe(feature) #feature type
			fc_type = desc.shapeType
			arcpy.AddMessage("Adding Mean High Water Field for water surface")
		
			#Add surface information by input type
			if fc_type == 'Point':
				arcpy.AddSurfaceInformation_3d(feature, mhw_surface, "Z", "LINEAR")
			elif fc_type == 'Polyline':
				arcpy.AddSurfaceInformation_3d(feature, mhw_surface, "Z_MEAN", "LINEAR")
				try:
					arcpy.AlterField_management(feature, "Z_MEAN", "Z", "Z") # change field name to "Z"
				except:
					change_fieldname(feature, "Z_MEAN", "Z")
			else:
				arcpy.AddError("Issue: Feature type not supported. Only convert lines or points!")
		
			#change surface info field name
			try: #attempts to change field using alter_field (arcgis v10.2.1+)
				arcpy.AlterField_management(feature, "Z", "WS_MHW_m", "WS_MHW_m") # changes field name
			except: #if alterfield does not work. Slower then alter field method for compatibility
				change_fieldname(feature, "Z", "WS_MHW_m")
				
			#Add field with raster name for conversion surface
			
			arcpy.AddField_management(feature, "Tidal_Datum_Source", "TEXT")
			arcpy.CalculateField_management(feature, "Tidal_Datum_Source", '"' + mhw_surface + '"', "PYTHON_9.3")
				
			#add field to calculate NAVD88 from sounding and mhw_m
			arcpy.AddField_management(feature, "NAVD88_m", "DOUBLE")
			arcpy.CalculateField_management(feature, "NAVD88_m", "!WS_MHW_m! + !MHW_m!", "PYTHON_9.3") #check!!
			arcpy.AddMessage("Calculating NAVD88 Elevation")
		else:
			arcpy.AddError("Issue: fields already exist for feature. Delete problem fields and try again")
			break


except arcpy.ExecuteError:
	print arcpy.GetMessages()