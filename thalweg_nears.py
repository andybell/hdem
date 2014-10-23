__author__ = 'ambell'


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


# changes negative and large angles to 0-360 degrees with 0 = due east
def change_angle(angle):
	if 0 > angle > -180:
		return angle + 360
	elif 0 <= angle < 360:
		return angle
	else:
		return change_angle(angle % 360)


# search for nearest feature within limits
def opposite_search_limits(near_angle):  # change name to search opposite limits?
	nearest = change_angle(near_angle)
	limit1 = change_angle(nearest + 135)
	limit2 = change_angle(nearest + 225)
	return limit1, limit2


def search_opposite(target_feature, near_features):
	#select features within limit (or delete rows that are outside of limits)?
	#then, within selection get the closest (or delete others)
	#return as opposite bank
	near_table = "in_memory" + "\\" + "near_temp" # TODO: double check that this works!!!
	arcpy.GenerateNearTable_analysis(target_feature, near_features, near_table, "500 Meters", location="LOCATION",
									angle="ANGLE", closest="ALL", closest_count = "100)
	arcpy.Delete_management("in_memory")
	pass

	


	
	
# get list of unique values in a table 
def unique_values(table, field):
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor})
	
def cursor_angle_search(near_table):
	FID_list = unique_values(near_table, "IN_FID")
	for i in FID_list:
		print i
		# Create the search cursor
		cursor = arcpy.SearchCursor(near_table, '"IN_FID"' + '=' +  str(i))
		#closest feature angle
		angle1 = [] 
		# Iterate through the rows in the cursor
		for row in cursor:
			if angle1 is None:
				angle1 = row.getValue("NEAR_ANGLE")
			else:
				pass
			#print(row.NEAR_ANGLE)
		del cursor, row
		print angle1
	
	
	
#creating line from two points
for row in feature: #or something
	arcpy.Array(pnt1, pnt2)## or something
	
	
	
	
near_table = 'near_table'
i = 1
cursor = arcpy.SearchCursor(near_table, '"IN_FID"' + '=' +  str(i))	

for row in cursor:
	print row.getValue("NEAR_ANGLE")