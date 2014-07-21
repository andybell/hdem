#-------------------------------------------------------------------------------
# Name: change_z.py	
# Purpose: converts field name from z to something else
# Author: Andy Bell (ambell@ucdavis.edu) 
# Created: 7/18/2014
#-------------------------------------------------------------------------------

import arcpy
from arcpy import env

GDB = r"U:\HDEM_v3_1\TIN_inputs_v3_NADV88.gdb"
env.workspace = GDB

print GDB

#alter field name from 'z' to another field name
def change_fn_z(fc, newname, newali):
	fieldList = arcpy.ListFields(fc) #get list of fields for a fc
	for field in fieldList: # loop through each field
		if field.name.upper() == 'Z': # look for field name 
			arcpy.AlterField_management(fc, field.name, newname, newali)
			print "Changing 'Z' to %s" % newname
			
#change all the features in a geodatabase

fclist = arcpy.ListFeatureClasses()

for feature in fclist:
	print feature
	change_fn_z(feature, 'MLLW_m', 'MLLW_m')


