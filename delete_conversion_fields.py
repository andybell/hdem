#-------------------------------------------------------------------------------
# Name: delete_conversion_fields.py
# Purpose: deletes conversion fields from all features
# Author: Andy Bell (ambell@ucdavis.edu)
# Created: 7/19/2014
#-------------------------------------------------------------------------------

import arcpy
from arcpy import env

#check fieldnames for reserved names: "MSL_m" "Tidal_range_m" "NAVD88m"
reserved = ['MSL_m', 'Tidal_Range_m', 'NAVD88_m', 'WS_MLLW_m']

# get list of features
inString = arcpy.GetParameterAsText(0)
fcList = inString.split(";")

# interate over feature list and change field names

# use extract values to points instead of addsurfaceinformation_3d
for feature in fcList:
	arcpy.AddMessage(feature) #adds feature name to output

	fieldList = arcpy.ListFields(feature)
	for field in fieldList:
		if field.name in reserved:
			arcpy.AddMessage("Deleting Reserved Fieldname: %s" %(field.name))
			arcpy.DeleteField_management(feature, field.name)