__author__ = 'Andy'

# originally from gen_parabolas.py but not used.

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

