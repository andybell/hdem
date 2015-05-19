__author__ = 'ambell'

import arcpy
import parabola  # imports functions from parabola.py
import csv
import os
import subprocess
import tempfile
import shutil
import config  # imports configuration settings


def addfields(target_table, name_list):
	"""Adds new fields from a list as doubles"""
	for name in name_list:
		arcpy.AddField_management(target_table, name, "DOUBLE")


def nearTable(thalweg_pts, channel_pts, target_dbf):
	"""Creates a near table to find the all near points on the bank from the thalweg including loc and angle"""
	# target_dbf = os.path.join(dirpath, "Input_Near_Table.dbf")
	arcpy.GenerateNearTable_analysis(thalweg_pts, channel_pts, target_dbf, "#",
	                                 "LOCATION", "ANGLE", "ALL", 200)


def near180_subprocess(dirpath, bind):
	"""subprocess call to R to run Near180.py to find two closest points (one on each bank)"""
	"""bind can either be 'APPEND' or 'MERGE'"""
	# location of R output dbf file
	input_dbf = os.path.join(dirpath, "Input_Near_Table.dbf")
	# near180 = r"C:\Users\Andy\Documents\hdem\R_HDEM\Near180.R"  # TODO change to be universal?
	near180 = os.path.join(os.path.dirname(__file__), 'Near180.R')
	# rscript_path = r"C:\Program Files\R\R-3.1.2\bin\rscript.exe"  # TODO universal?
	rscript_path = config.rscript_path  # location of the R executable
	rlib = config.r_lib_loc  # location of the R library

	print "Calling {} {} --args {} {}".format(rscript_path, near180, input_dbf, dirpath, bind, rlib)  # add bind
	# Subprocess call out to R to run Near180.R functions to reduce near table to two closest records
	subprocess.call([rscript_path, near180, "--args", input_dbf, dirpath, bind, rlib])


def join_z_neartable(near_dbf, target_features, depth_field, objectid_field):
	"""Joins depth field to the near table"""
	# Add field for join (THALWEG_Z and BANK_Z as doubles)
	new_fields = ["THALWEG_Z", "BANK_Z"]
	addfields(near_dbf, new_fields)

	# join on thalweg_pts unique IDs
	arcpy.JoinField_management(near_dbf, "IN_FID", target_features, objectid_field)

	# Calculate fields
	arcpy.CalculateField_management(near_dbf, "THALWEG_Z", '!' + depth_field + '!', "PYTHON_9.3")

	# remove join by dropping unwanted fields
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

	# export to csv/txt and then add points via arc xy to points tool
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
	sp_ref = r"Coordinate Systems\Projected Coordinate Systems\Utm\Nad 1983\NAD 1983 UTM Zone 10N.prj"
	arcpy.MakeXYEventLayer_management(xy_txt, 'Field1', 'Field2', 'outlyr', sp_ref)
	arcpy.FeatureClassToFeatureClass_conversion('outlyr', output_gdb, output_name)
	arcpy.Delete_management('outlyr')


def alt_fields(feature, z_field):
	"""changes the field names"""
	arcpy.AlterField_management(feature, 'Field1', 'X', 'X')
	arcpy.AlterField_management(feature, 'Field2', 'Y', 'Y')
	arcpy.AlterField_management(feature, 'Field3', z_field, z_field)


def make_points(thalweg_points, thalweg_fid, thalweg_z, banks_as_points, output):
	"""
	make_points function that batches all the steps, input is features for near table, output is location for parabola pts
	:param thalweg_points: points that are on the thalweg of the channel. Must have a value for depth.
	:param thalweg_fid: OBJECTID field in thalweg_points
	:param thalweg_z: depth field in thalweg_points	(likely MLLW_m)
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
	join_z_neartable(os.path.join(dirpath, "both_banks.dbf"), thalweg_points, thalweg_fid, thalweg_z)

	print "Generating parabola POINTS!!!"
	gen_pts_nears(os.path.join(dirpath, "both_banks.dbf"), dirpath)

	print "Saving to gdb"
	pathname = os.path.split(output)

	xy_to_pts(os.path.join(dirpath, "parabola_points.txt"), pathname[0], pathname[1])
	print "Changing field names"
	alt_fields(output, thalweg_z)
	print "Removing duplicate points"
	arcpy.DeleteIdentical_management(output, ["X", "Y", thalweg_z])

	print "Removing Temporary Files"
	# remove the temporary directory
	shutil.rmtree(dirpath)
