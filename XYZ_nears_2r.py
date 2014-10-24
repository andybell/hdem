# some usefull python snippets for coping near feature to r

# add double fields for items in the list
def addfields(target_table, name_linst):
	for name in name_list:
		arcpy.AddField_management(target_table, name, "DOUBLE")


def alter_fields(table, name_dict):
	for key in name_dict:
		arcpy.AlterField_management(table, name_dict[key], key, key)
	

# generate near table with location and angle and then join original fid to prime_feature coords
# save as dbf for r to open???
def near_table(prime_feature, near_features, near_table):
	#near_table = r"in_memory\temp" # TODO: double check that this works!!!
	arcpy.GenerateNearTable_analysis(prime_feature, near_features, near_table, "500 Meters", location="LOCATION",
									angle="ANGLE", closest="ALL", closest_count=50)
	arcpy.JoinField_management(near_table, "IN_FID", prime_feature, "OBJECTID")


# delete unneccesary fields
def keep_mandatory_fields(table):
	mandatory_field_list = ["OBJECTID", "X1", "Y1", "Z1", "X2", "Y2", "Z2", "NEAR_DIST", "NEAR_RANK", "NEAR_ANGLE", "IN_FID"]
	field_list = arcpy.ListFields(table)
	for field in field_list:
		print field.name
		if field.name in mandatory_field_list:
			pass
		else:
			arcpy.DeleteField_management(table, field.name)
		
	
	
# Example for whiskey slough!!!!
# python dictionary with name change, new values should be the key and old the vaules
whiskey = ''
channels = ''

whiskey_dict = {"X1":"ET_X", "Y1":"ET_Y", "X2":"NEAR_X", "Y2":"NEAR_Y"}

alter_fields(whiskey, whiskey_dict)

keep_mandatory_fields(whiskey)

near_table(whiskey, channels)




