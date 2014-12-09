__author__ = 'ambell'

import arcpy
import parabola

# input near table with values for x sections with thalweg and bank Z's joined
inNearTable = r"X:\delta_dem\HDEM_v5r1\NearTable_sounds_channel.gdb\Near180_xsections_500features"

# Destination Feature Class for the points
# Feature MUST have a field called "MLLW_m" as double
pointFC = r"U:\HDEM_v5r1\tester.gdb\Sounding_XS"  # should this be run as a tool or a stand alone script?


#parse fields
fields = ['FROM_X', 'FROM_Y', 'Thalweg_Z', 'NEAR_X', 'NEAR_Y', 'Bank_Z']

end_pt_list = []

print "Reading rows from the Near Table....."
with arcpy.da.SearchCursor(inNearTable, fields) as cursor:
	for row in cursor:
		thalweg = (row[0], row[1], row[2])
		bank = (row[3], row[4], row[5])
		pair = (thalweg, bank)
		end_pt_list.append(pair)
del cursor

counter = 1

#TODO insert TIMEIT or datetime to profile how long functions take

#TODO backup plan remove cursor and export to csv/txt and then add points via arc xy to points tool

for point in end_pt_list:
	print "Working on X section: %s" %counter
	parabola_points = parabola.gen_pts(point[0], point[1])

	cursor = arcpy.da.InsertCursor(pointFC, ['SHAPE@X', 'SHAPE@Y', 'MLLW_m'])
	for new_point in parabola_points:
		row = [new_point[0], new_point[1], new_point[2]]
		cursor.insertRow(row)
	del cursor
	counter = counter + 1


print "Finished!!!!!"