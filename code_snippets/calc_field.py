__author__ = 'ambell'

#linear regression to use for setting depths for hdem using field calculation codeblock. Must have a field with river distance (station_points)

def rm_regression(distance_field, start_distance, end_distance, start_z, end_z):
	if start_distance <= distance_field <= end_distance:
		depth = start_z + ((distance_field -start_distance) * (end_z - start_z)/(end_distance - start_distance))
		return depth
