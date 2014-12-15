__author__ = 'ambell'

import arcpy
import parabola
import csv
import os
import subprocess
import tempfile
import shutil

def addfields(target_table, name_list):
	for name in name_list:
		arcpy.AddField_management(target_table, name, "DOUBLE")


def nearTable(thalweg_pts, channel_pts):
	target_dbf = os.path.join(dirpath, "Input_Near_Table.dbf")
	arcpy.GenerateNearTable_analysis(thalweg_pts, channel_pts, target_dbf, "#",
	                                 "LOCATION", "ANGLE", "ALL", 200)


def join_z_neartable(near_dbf, target_features, depth_field):

	#Add field for join (THALWEG_Z and BANK_Z as doubles)
	new_fields = ["THALWEG_Z", "BANK_Z"]
	addfields(near_dbf, new_fields)

	#join on thalweg_pts unique IDs
	arcpy.JoinField_management(near_dbf, "IN_FID", target_features, "OBJECTID")

	#Calculate fields
	arcpy.CalculateField_management(near_dbf, "THALWEG_Z", '!' + depth_field + '!', "PYTHON_9.3")

	#remove join by dropping unwanted fields
	fields2keep = ["OID", "THALWEG_Z", "BANK_Z", "IN_FID", "NEAR_FID", "NEAR_DIST", "NEAR_RANK", "FROM_X", "FROM_Y", "NEAR_X", "NEAR_Y", "NEAR_ANGLE"]

	fields = arcpy.ListFields(near_dbf)

	for field in fields:
		if field.name in fields2keep:
			pass
		else:
			arcpy.DeleteField_management(near_dbf, field.name)


def near180_subprocess(dirpath):

	#location of R output dbf file
	input_dbf = os.path.join(dirpath, "Input_Near_Table.dbf")
	near180 = r"C:\Users\ambell.AD3\Documents\hdem\R_HDEM\Near180.R" # TODO change to be universal?
	rscript_path = r"C:\Users\ambell.AD3\Documents\R\R-3.1.2\bin\rscript.exe" # TODO universal?


	print "Calling {} {} --args {} {}".format(rscript_path, near180, input_dbf, dirpath)
	#Subprocess call out to R to run Near180.R functions to reduce near table to two closest records
	subprocess.call([rscript_path, near180, "--args", input_dbf, dirpath])


def gen_pts_nears(inNearTable_withZ, out_directory):
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
	out_txt = os.path.join(out_directory, "parabola_points.txt") # TODO: need separate files for near + opposite?
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


def xy_to_pts(xy_txt, output):
	arcpy.MakeXYEventLayer_management(xy_txt)
	pass


#Tester files
thalweg_pts = r"U:\HDEM_v5r1_120914\Suisun_working_v5r1.gdb\Suisun_small_channel_soundings_h00948"
banks_as_pts = r"U:\HDEM_v5r1_120914\Channel_pts_5m_GME_no_dups.shp"



#make temp directory to store all interim data steps
dirpath = tempfile.mkdtemp()



print "Finding lots of nearest features....."
nearTable(thalweg_pts, banks_as_pts)

print "Finding two closest features on opposite banks (Near180.r)..."
near180_subprocess(dirpath)

print "Joining thalweg depths...."
join_z_neartable(os.path.join(dirpath, "nearest_bank.dbf"), thalweg_pts, "MLLW_m")
join_z_neartable(os.path.join(dirpath, "opposite_bank.dbf"), thalweg_pts, "MLLW_m")

print "Generating parabola POINTS!!!"
gen_pts_nears(os.path.join(dirpath, "nearest_bank.dbf"), dirpath)

print "Temporary Directory: %s" % dirpath