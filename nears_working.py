# get list of unique values in a table 
def unique_values(table, field):
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor})
	
def cursor_angle_search(near_table):
	FID_list = unique_values(near_table, "IN_FID")
	for i in FID_list:
		print i
		temp_table = "in_memory" + "\\" + "atable_" + str(i)
		arcpy.MakeTableView_management(near_table, temp_table, '"IN_FID"' + '=' +  str(i))
		arcpy.Delete_management("in_memory")
		
		
		
		
		# Create the search cursor
		cursor = arcpy.SearchCursor(near_table, )
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

memoryFeature = "in_memory" + "\\" + "myMemoryFeature"
arcpy.Delete_management("in_memory")


MakeTableView_management (in_table, out_view, {where_clause}, {workspace}, {field_info})
Sort_management (in_dataset, out_dataset, sort_field, {spatial_sort_method})

