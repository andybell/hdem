#-------------------------------------------------------------------------------
# Name: conversion_arcpy.py	
# Purpose: converts points from mllw to NAVD88 based on tidal range and msl
# Author: Andy Bell (ambell@ucdavis.edu) 
# Created: 7/18/2014
#-------------------------------------------------------------------------------

import arcpy
from arcpy import env
import exceptions, sys, traceback


#check fieldnames for reserved names: "MSL_m" "Tidal_range_m" "NADV88m"
def check_fieldnames(fc):
	fieldList = arcpy.ListFields(fc)
	reserved = ['MSL_m', 'Tidal_Range_m', 'NAVD88_m']
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
	env.workspace = arcpy.GetParameterAsText(0)
	msl_surface = arcpy.GetParameterAsText(1)
	tidal_range_surface = arcpy.GetParameterAsText(2)
	MLLW_name = arcpy.GetParameterAsText(3) # field name for column with MLLW
	MLLW2MSL_NAVD88 = arcpy.GetParameterAsText(4) # option to calculate MLLW2MSL
	MLLW2MHHW_NADV88 = arcpy.GetParameterAsText(5) # option to calculate MLLW2MHHW
	
	arcpy.AddMessage(MLLW_name)
	arcpy.AddMessage(MLLW2MSL_NAVD88)
	arcpy.AddMessage(MLLW2MHHW_NADV88)
	
	# get list of features
	inString = arcpy.GetParameterAsText(0)
	fcList = inString.split(";") #splits input string into a list of features
	
	arcpy.AddMessage(fcList)

	# interate over feature list and change field names 
	# use extract values to points instead of addsurfaceinformation_3d
	for feature in fcList:
		arcpy.AddMessage(feature) #adds feature name to output
		
		#checks if feature contains reserved field names
		if check_fieldnames(feature) == False:
			arcpy.AddError("Issue: fields already exist for feature. Delete problem fields and try again")
			break
		
		#feature type
		desc = arcpy.Describe(feature)
		fc_type = desc.shapeType
		arcpy.AddMessage(fc_type)
		
		#do stuff based on input type
		if fc_type == 'Point':
				
			#field with MSL
			arcpy.AddMessage("Adding Mean Sea Level Surface Field")
			arcpy.AddSurfaceInformation_3d(feature, msl_surface, "Z", "LINEAR")
			try: #attempts to change field using alter_field (arcgis v10.2.1+)
				arcpy.AlterField_management(feature, "Z", "MSL_m", "MSL_m") # changes field name
			except: #if alterfield does not work. Slower then alter field method for compatibility
				change_fieldname(feature, "Z", "MSL_m")
					
			#field with tidal range
			arcpy.AddMessage("Adding Tidal Range Field")
			arcpy.AddSurfaceInformation_3d(feature, tidal_range_surface, "Z", "LINEAR")
			try: #attempts to change field using alter_field (arcgis v10.2.1+)
				arcpy.AlterField_management(feature, "Z", "Tidal_Range_m", "Tidal_Range_m") # changes field name
			except: #if alterfield does not work. Slower then alter field method for compatibility
				change_fieldname(feature, "Z", "Tidal_Range_m")
				
		elif fc_type == 'Polyline':
		
			#field with MSL
			arcpy.AddMessage("Adding Mean Sea Level Surface Field")
			arcpy.AddSurfaceInformation_3d(feature, msl_surface, "Z_MEAN", "LINEAR")
			try: #attempts to change field using alter_field (arcgis v10.2.1+)
				arcpy.AlterField_management(feature, "Z_MEAN", "MSL_m", "MSL_m") # changes field name
			except: #if alterfield does not work. Slower then alter field method for compatibility
				change_fieldname(feature, "Z_MEAN", "MSL_m")
				
			#field with tidal range
			arcpy.AddMessage("Adding Tidal Range Field")
			arcpy.AddSurfaceInformation_3d(feature, tidal_range_surface, "Z_MEAN", "LINEAR")
			try: #attempts to change field using alter_field (arcgis v10.2.1+)
				arcpy.AlterField_management(feature, "Z_MEAN", "Tidal_Range_m", "Tidal_Range_m") # changes field name
			except: #if alterfield does not work. Slower then alter field method for compatibility
				change_fieldname(feature, "Z_MEAN", "Tidal_Range_m")
				
		else:
			arcpy.AddError("Issue: Feature type not supported. Only convert lines or points!")
			break
			
		#add field to calculate NAVD88 for mllw_m, tidal_range_m and MSL_m
		if str(MLLW2MSL_NAVD88) == 'true':
			arcpy.AddField_management(feature, "NAVD88_m", "DOUBLE")
			arcpy.CalculateField_management(feature, "NAVD88_m", "!MSL_m! + (MLLW_name + !Tidal_Range_m!/2)", "PYTHON_9.3")
			arcpy.AddMessage("Calculating NAVD88 Elevation from 1/2 tidal range and mean sea level")
		
		#add field to calculate NAVD88 for mllw_m, tidal_range_m and MSL_m
		if str(MLLW2MHHW_NADV88) == 'true':
			arcpy.AddField_management(feature, "NAVD88_m_MHHW", "DOUBLE")
			arcpy.CalculateField_management(feature, "NAVD88_m_MHHW", "!MSL_m! + '!' + MLLW_name + '!' + !Tidal_Range_m!", "PYTHON_9.3")
			arcpy.AddMessage("Calculating Elevation from full tidal range and mean sea level")
		
		

except arcpy.ExecuteError:
	print arcpy.GetMessages()