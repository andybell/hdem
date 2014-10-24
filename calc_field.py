__author__ = 'ambell'

#linear regression to use for setting depths for hdem using field calculation codeblock. Must have a field with river distance (station_points)

def rm_regression(distance_field, start_distance, end_distance, start_z, end_z):
	if start_distance <= distance_field <= end_distance:
		depth = start_z + ((distance_field -start_distance) * (end_z - start_z)/(end_distance - start_distance))
		return depth


ca_dict =	{'Y1': 'ET_Y', 'X2': 'NEAR_X', 'X1': 'ET_X', 'Z1': 'MLLW_m', 'Y2': 'NEAR_Y'}