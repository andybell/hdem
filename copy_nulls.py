import arcpy, os

from arcpy import env

env.workspace = r"U:\HDEM_v3r1\TIN_inputs_v3r1_NADV88.gdb"
fcList = arcpy.ListFeatureClasses()
output_nulls = r"U:\HDEM_v3r1\NADV88_nulls.gdb"



for feature in fcList:
	print feature
	arcpy.SelectLayerByAttribute_management (feature, "NEW_SELECTION", "NAVD88_m is Null")
	num_selected = arcpy.GetCount_management(feature)
	if num_selected > 1:
		print "Number of Nulls:"
		print num_selected
		#arcpy.CopyFeatures_management(feature, os.path.join(output_nulls, feature))
	else:
		print "No null values"