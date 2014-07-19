#-------------------------------------------------------------------------------
# Name: conversion_arcpy.py	
# Purpose: converts points from mllw to NAVD88 based on tidal range and msl
# Author: Andy Bell (ambell@ucdavis.edu) 
# Created: 7/18/2014
#-------------------------------------------------------------------------------

import arcpy
from arcpy import env
import exceptions, sys, traceback

#alter field name from 'z' to another field name
def change_fn_z(fc, newname, newali):
	fieldList = arcpy.ListFields(fc) #get list of fields for a fc
	for field in fieldList: # loop through each field
		if field.name.upper() == 'Z': # look for field name 
			arcpy.AlterField_management(fc, field.name, newname, newali)
			print "Changing 'Z' to %s" % newname

try:
	arcpy.CheckOutExtension("3D")
	# Set Local Variables
	env.workspace = arcpy.GetParameterAsText(0)
	msl_surface = arcpy.GetParameterAsText(1)
	tidal_range_surface = arcpy.GetParameterAsText(2)
	
	# get list of features
	fcList = arcpy.ListFeatureClasses()

	# interate over feature list and change field names 
	# currently on works for points. 
	# TODO: add if statement to deal with lines separately
	# TODO: lines fishnet? or split by segment?
	# use extract values to points instead of addsurfaceinformation_3d
	for feature in fcList:
		arcpy.AddMessage(feature) #adds feature name to output
		
		# change z field in feature to mllw
		change_fn_z(feature, "MLLW_m", "MLLW_meters") 
		arcpy.AddMessage("Changing FieldName")
		
		#field with MSL
		arcpy.AddMessage("Adding Mean Sea Level Surface info")
		arcpy.AddSurfaceInformation_3d(feature, msl_surface, "Z", "LINEAR")
		change_fn_z(feature, "MSL_m", "MSL_m")
		arcpy.AddMessage("Changing Z to MSL_m")
		
		#field with MSL
		arcpy.AddMessage("Adding Tidal Range info")
		arcpy.AddSurfaceInformation_3d(feature, tidal_range_surface, "Z", "LINEAR")
		change_fn_z(feature, "Tidal_Range_m", "Tidal_Range_m")
		arcpy.AddMessage("Changing Z to Tidal_Range_m")
		
		#add field to calculate NAVD88 for mllw_m, tidal_range_m and MSL_m
		arcpy.AddField_management(feature, "NAVD88_m", "DOUBLE")
		arcpy.CalculateField_management(feature, "NAVD88_m", "!MSL_m! + (!MLLW_m!+!Tidal_Range_m!/2)", "PYTHON_9.3")
		arcpy.AddMessage("Calculating NAVD88 Elevation from tidal raster and mean sea level")
		

except arcpy.ExecuteError:
	print arcpy.GetMessages()