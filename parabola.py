__author__ = 'ambell'

import math

#python parabola formulas for cross section area


def cross_section_area(parabola1, parabola2):
	x_area = parabola1 + parabola2 # cross section area is the sum of the two parabola curves
	return x_area


def ThreeD_distance(point1, point2):
	# points are truples that contain (x,y,z)'s
	x1 = point1[0]
	y1 = point1[1]
	z1 = point1[2]
	x2 = point2[0]
	y2 = point2[1]
	z2 = point2[2]

	distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)
	return distance


def TwoD_distance(point1, point2):
	# points are truples that contain (x,y,z)'s
	x1 = point1[0]
	y1 = point1[1]
	#z1 = point1[2]
	x2 = point2[0]
	y2 = point2[1]
	#z2 = point2[2]

	distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
	return distance


def half_parabola_depth(point1, point2, location_on_line):
	z1 = point1[2]
	z2 = point2[2]

	if z1 > z2:
		bank_z = z1
		thalweg_z = z2
	else:
		bank_z = z2
		thalweg_z = z1

	depth_at_location = (bank_z-thalweg_z) / (ThreeD_distance(point1, point2)) ** 2 * location_on_line ** 2 + thalweg_z

	return depth_at_location


def parabola_area(point1, point2):
	z1 = point1[2]
	z2 = point2[2]

	if z1 > z2:
		bank_z = z1
		thalweg_z = z2
	else:
		bank_z = z2
		thalweg_z = z1

	print "bank: %s" %bank_z
	print "thalweg: %s" %thalweg_z

	area = float(2) / 3 * (bank_z - thalweg_z) * TwoD_distance(point1, point2)

	return area


#example points
test1 = [624377.695892, 4212225.53683, -5.0292]
test2 = [624491.335396, 4212201.91912, 0.0]


dist2d = TwoD_distance(test1,test2)
dist3d = ThreeD_distance(test1,test2)

print dist2d, dist3d

test_area = parabola_area(test1, test2)

print test_area