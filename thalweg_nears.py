__author__ = 'ambell'


import arcpy

# purpose is to join the nearest channel and then the second nearest channel feature to the thalweg


#1. copy thalweg file to create a near bank
#2. for near bank all we have to do is generate a near table and join the attribute to the original
#4. copy thalweg file for far bank
#5. for the far bank we need to search 180 degrees away from the near bank, locate closest and then join to original


# original point on thalweg should have X1, Y1, Z1

# add X2, Y2, Z2 for nearest point
def addfields(target_table):
	arcpy.AddField_management(target_table, "X2","DOUBLE")
	arcpy.AddField_management(target_table, "Y2", "DOUBLE")
	arcpy.AddField_management(target_table, "Z2", "DOUBLE")


def join_copy(target_feature, target_field, join_table, join_field, fields):

	arcpy.JoinField_management(target_feature, target_feature, join_table, join_field)


# function to create the only the nearest feature -> should return a table that will be joined to the thalweg
def join_nearest(target_feature, target_FID, near_features):
	#need to create a temporary out_table?
	arcpy.GenerateNearTable_analysis(target_feature, near_features, near_table, location="LOCATION",
	                                 angle="ANGLE", closest="CLOSEST")

	arcpy.JoinField_management(target_feature, target_FID, near_table,"IN_FID", ["NEAR_X", "NEAR_Y", "NEAR_ANGLE"])



def generate_many_nears():
	something









