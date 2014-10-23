# import arcpy

# purpose is to join the nearest channel and then the second nearest channel feature to the thalweg
# 1. copy thalweg file to create a near bank
#2. for near bank all we have to do is generate a near table and join the attribute to the original
#4. copy thalweg file for far bank
#5. for the far bank we need to search 180 degrees away from the near bank, locate closest and then join to original

# original point on thalweg should have X1, Y1, Z1

# add X2, Y2, Z2 for nearest point
def addfields(target_table):
	arcpy.AddField_management(target_table, "X2", "DOUBLE")
	arcpy.AddField_management(target_table, "Y2", "DOUBLE")
	arcpy.AddField_management(target_table, "Z2", "DOUBLE")


# function to create the only the nearest feature -> should return a table that will be joined to the thalweg
def join_nearest(target_feature, target_FID, near_features):
	#need to create a temporary out_table?
	near_table = r"in_memory\temp" # TODO: double check that this works!!!
	arcpy.GenerateNearTable_analysis(target_feature, near_features, near_table, location="LOCATION",
									angle="ANGLE", closest="CLOSEST")

	arcpy.JoinField_management(target_feature, target_FID, near_table, "IN_FID", ["NEAR_X", "NEAR_Y", "NEAR_ANGLE"])
	
	
# generate near table with location and angle (50)?
# modify field names to x2, y2, z2, 
# join back to original fid to get x1,y1,z1
# save as dbf for r to open???

arcpy.GenerateNearTable_analysis(target_feature, near_features, near_table, "500 Meters", location="LOCATION",
									angle="ANGLE", closest="ALL", closest_count = "50)
									
arcpy.JoinField_management(near_table, "IN_FID", target_feature, "OBJECTID", ["X1", "Y1", "Z1"])