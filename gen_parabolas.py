__author__ = 'ambell'

import arcpy
import parabola  # imports functions from parabola.py
import csv
import os
import subprocess
import tempfile
import shutil


def addfields(target_table, name_list):
	"""Adds new fields from a list as doubles"""
	for name in name_list:
		arcpy.AddField_management(target_table, name, "DOUBLE")


def nearTable(thalweg_pts, channel_pts, target_dbf):
	"""Creates a near table to find the all near points on the bank from the thalweg including loc and angle"""
	#target_dbf = os.path.join(dirpath, "Input_Near_Table.dbf")
	arcpy.GenerateNearTable_analysis(thalweg_pts, channel_pts, target_dbf, "#",
	                                 "LOCATION", "ANGLE", "ALL", 200)


def near180_subprocess(dirpath, bind):
	"""subprocess call to R to run Near180.py to find two closest points (one on each bank)"""
	"""bind can either be 'APPEND' or 'MERGE'"""
	#location of R output dbf file
	input_dbf = os.path.join(dirpath, "Input_Near_Table.dbf")
	near180 = r"C:\Users\Andy\Documents\hdem\R_HDEM\Near180.R"  # TODO change to be universal?
	rscript_path = r"C:\Program Files\R\R-3.1.2\bin\rscript.exe"  # TODO universal?

	print "Calling {} {} --args {} {}".format(rscript_path, near180, input_dbf, dirpath)  # add bind
	#Subprocess call out to R to run Near180.R functions to reduce near table to two closest records
	subprocess.call([rscript_path, near180, "--args", input_dbf, dirpath, bind])


def join_z_neartable(near_dbf, target_features, depth_field):
	"""Joins depth field to the near table"""
	#Add field for join (THALWEG_Z and BANK_Z as doubles)
	new_fields = ["THALWEG_Z", "BANK_Z"]
	addfields(near_dbf, new_fields)

	#join on thalweg_pts unique IDs
	arcpy.JoinField_management(near_dbf, "IN_FID", target_features, "OBJECTID")

	#Calculate fields
	arcpy.CalculateField_management(near_dbf, "THALWEG_Z", '!' + depth_field + '!', "PYTHON_9.3")

	#remove join by dropping unwanted fields
	fields2keep = ["OID", "THALWEG_Z", "BANK_Z", "IN_FID", "NEAR_FID", "NEAR_DIST", "NEAR_RANK", "FROM_X", "FROM_Y",
	               "NEAR_X", "NEAR_Y", "NEAR_ANGLE"]

	fields = arcpy.ListFields(near_dbf)

	for field in fields:
		if field.name in fields2keep:
			pass
		else:
			arcpy.DeleteField_management(near_dbf, field.name)


def gen_pts_nears(inNearTable_withZ, out_directory):
	"""generates points from the near table with values for the thalweg and banks using parabola calcs"""
	fields = ['FROM_X', 'FROM_Y', 'THALWEG_Z', 'NEAR_X', 'NEAR_Y', 'BANK_Z']

	end_pt_list = []  # empty list to store points

	print "Reading rows from the Near Table....."
	with arcpy.da.SearchCursor(inNearTable_withZ, fields) as cursor:
		for row in cursor:
			thalweg = (row[0], row[1], row[2])
			bank = (row[3], row[4], row[5])
			pair = (thalweg, bank)
			end_pt_list.append(pair)
	del cursor

	#export to csv/txt and then add points via arc xy to points tool
	out_txt = os.path.join(out_directory, "parabola_points.txt")  # TODO: need separate files for near + opposite?
	txtfile = open(out_txt, 'w')
	writer = csv.writer(txtfile)

	rows = []
	counter = 1

	for point in end_pt_list:
		if counter % 100 == 0:
			print "Working on X section: %s" % counter
		parabola_points = parabola.gen_pts(point[0], point[1])
		counter += 1

		for new_point in parabola_points:
			row = [new_point[0], new_point[1], new_point[2]]
			rows.append(row)

	writer.writerows(rows)
	txtfile.close()


def xy_to_pts(xy_txt, output_gdb, output_name):
	"""converts text file to feature class"""
	sp_ref = r"Coordinate Systems\Projected Coordinate Systems\Utm\Nad 1983\NAD 1983 UTM Zone 10N.prj" # this might be a hard REF!!!!
	arcpy.MakeXYEventLayer_management(xy_txt, 'Field1', 'Field2', 'outlyr', sp_ref)
	arcpy.FeatureClassToFeatureClass_conversion('outlyr', output_gdb, output_name)


def alt_fields(feature):
	"""changes the field names"""
	arcpy.AlterField_management(feature, 'Field1', 'X', 'X')
	arcpy.AlterField_management(feature, 'Field2', 'Y', 'Y')
	arcpy.AlterField_management(feature, 'Field3', 'MLLW_m', 'MLLW_m')


def make_points(thalweg_points, banks_as_points, output):
	"""
	make_points function that batches all the steps, input is features for near table, output is location for parabola pts
	:param thalweg_points: points that are on the thalweg of the channel. Must have a value for depth.
	:param banks_as_points: channel lines represented as points (pts on each bank every 5m)
	:param output: location for the output file for the geodatabase
	:return: parabola points generated as cross sections
	"""
	dirpath = tempfile.mkdtemp()

	print "Finding lots of nearest features....."
	nearTable(thalweg_points, banks_as_points, os.path.join(dirpath, "Input_Near_Table.dbf"))

	print "Finding two closest features on opposite banks (Near180.r)..."
	near180_subprocess(dirpath, "APPEND")

	print "Joining thalweg depths...."
	join_z_neartable(os.path.join(dirpath, "both_banks.dbf"), thalweg_points, "MLLW_m")

	print "Generating parabola POINTS!!!"
	gen_pts_nears(os.path.join(dirpath, "both_banks.dbf"), dirpath)

	print "Saving to gdb"
	pathname = os.path.split(output)

	xy_to_pts(os.path.join(dirpath, "parabola_points.txt"), pathname[0], pathname[1])
	print "Changing field names"
	alt_fields(output)
	print "Removing duplicate points"
	arcpy.DeleteIdentical_management(output, ["X", "Y", "MLLW_m"])

	print "Removing Temporary Files"
	# remove the temporary directory
	shutil.rmtree(dirpath)


"""
#Tester files
thalweg_pts = r"U:\HDEM_v5r3\suisun_transfer.gdb\suisun_centerlines_25m_no_nulls"
banks_as_pts = r"U:\HDEM_v5r3\Suisun_wateredge_densify.shp"
output = r"U:\HDEM_v5r3\suisun_transfer.gdb\Suisun_channels_parabolas"

make_points(thalweg_pts, banks_as_pts, output)
"""

#TODO number of samples to search table?
#TODO fix subprocess to make R independent of libraries/user paths.


#TODO FUNCTIONS to calculate x-section area -> depths. May need to just move to another script.
def join_near_table(input_points, dbf_xyz):
	"""joins the results from the NEAR180.R script with bind parameter 'MERGE' back to the original inputs"""

	pass


def calc_xsection_area(feature_with_xyz):
	"""feature class must have XYZ for bank1, bank2, and the thalweg. The XY for each of the points can be
		the result of join_near_table function but the elevations especially for the thalweg must be specified.
		Note: we are assuming that the elevation (z) for both banks is equal to the waterline (ie MLLW_m = 0)"""

	#expression = parabola.parabola_area(('!B1_X!', '!B1_Y!', 0), ('!T_X!', '!T_Y!', '!MLLW_m!')) + \
	            #parabola.parabola_area(('!B2_X!', '!B2_Y!', 0), ('!T_X!', '!T_Y!', '!MLLW_m!'))

	#arcpy.AddField_management(feature_with_xyz, "AREA", "DOUBLE")

	fields = ('AREA', 'B1_X', 'B1_Y', 'B2_X', 'B2_Y', 'T_X', 'T_Y', 'MLLW_m')

	with arcpy.da.UpdateCursor(feature_with_xyz, fields) as cursor:
		for row in cursor:
			row[0] = parabola.parabola_area((row[1], row[2], 0), (row[5], row[6], row[7])) + parabola.parabola_area((row[3], row[4], 0), (row[5], row[6], row[7]))
			cursor.updateRow(row)



def depth_from_area(feature_with_xy_and_xarea):
	"""input feature should have attributes with xy's for bank1, bank2, and thalweg point. Not necessarry to have depths
	for the points. The function should use the function parabola.depth_from_xsection(bank1, bank2, thalweg, x_section)
	to add estimated depths for each x-section triple"""
	
	fields = ('SPLINE_AREA', 'B1_X', 'B1_Y', 'B2_X', 'B2_Y', 'T_X', 'T_Y', 'MLLW_m')

	with arcpy.da.UpdateCursor(feature_with_xy_and_xarea, fields) as cursor:
		for row in cursor:
			row[7] = parabola.depth_from_xsection((row[1], row[2]), (row[3], row[4]), (row[5], row[6]), row[0]) 
			cursor.updateRow(row)


def spline_interp():
	"""figure out a way to include the spline interpolation using python. Look into the SciPy package (need to install
	since it is not a part of the python base package"""
	pass


def calc_xsection_area(feature_with_xyz):
	fields = ('AREA', 'B1_X', 'B1_Y', 'B2_X', 'B2_Y', 'T_X', 'T_Y', 'MLLW_m')

	with arcpy.da.UpdateCursor(feature_with_xyz, fields) as cursor:
		for row in cursor:
			row[0] = parabola.parabola_area((row[1], row[2], 0), (row[5], row[6], row[7])) + parabola.parabola_area((row[3], row[4], 0), (row[5], row[6], row[7]))
			cursor.updateRow(row)


in_feature = r"U:\HDEM_v5r3\Moke_xarea\Moke_pts_w_rivermile.shp"
calc_xsection_area(in_feature)