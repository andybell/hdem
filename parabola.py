__author__ = 'ambell'

import math

#python parabola formulas for cross section area, points need to be in the format of [x, y, z]


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

	#parabola x section area equal to 2/3 * change in height * distance
	area = float(2) / 3 * (bank_z - thalweg_z) * TwoD_distance(point1, point2)

	return area


def depth_from_xsection(bank1, bank2, thalweg, x_section):
	# bank1, bank2 are the closest points on the bank with [x, y, 0]'s. X_section is the cross area in m^2
	# want to set thalweg_z which is unknown from using the x-section area and parabola formula's

	total_distance = TwoD_distance(bank1, thalweg) + TwoD_distance(bank2, thalweg)

	#parabola x section area equal to 2/3 * change in height * distance
	#x_section = float(2)/3 * (bank_z - thalweg_z) * total_distance

	thalweg_z = -1 * x_section / total_distance * float(3) / 2

	return thalweg_z


