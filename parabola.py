__author__ = 'ambell'

import math

#python parabola formulas for cross section area, points need to be in the format of [x, y, z]


def ThreeD_distance(point1, point2):
	"""The 3D distance between two points (x,y,z) in space. Units must all be the same"""
	x1, y1, z1, x2, y2, z2 = point1[0], point1[1], point1[2], point2[0], point2[1], point2[2]
	distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)
	return distance


def TwoD_distance(point1, point2):
	"""The distance between points in two-dimensional space (ie ignoring any changes in Z's)"""
	x1, y1, x2, y2 = point1[0], point1[1], point2[0], point2[1]
	distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
	return distance


def CartesianToPolar(xy1, xy2):
	'''Given coordinate pairs as two lists or tuples, return the polar
	coordinates with theta in radians. Values are in true radians along the
	unit-circle, for example, 3.14 and not -0 like a regular python
	return.'''
	x1, y1, x2, y2 = float(xy1[0]), float(xy1[1]), float(xy2[0]), float(xy2[1])
	xdistance, ydistance = x2 - x1, y2 - y1
	#distance = math.pow(((math.pow((x2 - x1),2)) + (math.pow((y2 - y1),2))),.5)
	if xdistance == 0:
		if y2 > y1:
			theta = math.pi/2
		else:
			theta = (3*math.pi)/2
	elif ydistance == 0:
		if x2 > x1:
			theta = 0
		else:
			theta = math.pi
	else:
		theta = math.atan(ydistance/xdistance)
		if xdistance > 0 and ydistance < 0:
			theta = 2*math.pi + theta
		if xdistance < 0 and ydistance > 0:
			theta = math.pi + theta
		if xdistance < 0 and ydistance < 0:
			theta = math.pi + theta
	return theta


def half_parabola_depth(thalweg_pt, bank_pt, distance_between_pts):
	"""
	Generates depths at location between two points using a parabola function to set Z's
	:param thalweg_pt: XYZ of a point on the thalweg
	:param bank_pt: XYZ of point on the bank
	:param distance_between_pts: the distance between the two input points were a new point will be created
	:return: Depth (meters) of the parabola function at the location between the two points + XY
	"""

	x1, y1, z1, x2, y2, z2 = thalweg_pt[0], thalweg_pt[1], thalweg_pt[2], bank_pt[0], bank_pt[1], bank_pt[2]

	depth_at_location = (z2 - z1) / (ThreeD_distance(thalweg_pt, bank_pt)) ** 2 * distance_between_pts ** 2 + z1

	angle_between_points = CartesianToPolar((x1, y1), (x2, y2))

	# change in x is equal to cos(a) * hypo where a is the angle between pts (rad) and hypo is distance
	plus_x = distance_between_pts * math.cos(angle_between_points)

	# change in y is equal to sin(a) * hypo where a is the angle between pts (rad) and hypo is distance
	plus_y = distance_between_pts * math.sin(angle_between_points)

	x_new = x1 + plus_x
	y_new = y1 + plus_y
	z_new = depth_at_location

	new_point = (x_new, y_new, z_new)

	return new_point


def parabola_area(point1, point2):
	"""
	Calculates area under a parabola curve between two points.
	:param point1:
	:param point2:
	:return: area in square meters
	"""
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
	area = float(2) / 3 * (int(bank_z) - int(thalweg_z)) * TwoD_distance(point1, point2) # TODO: why is this int? shouldn't it be float????? Yikes!!!

	return area


def depth_from_xsection(bank1, bank2, thalweg, x_section):
	"""
	Calculate unknown max thalweg depth using interpolated the x_sectional area values

	:param bank1: point on bank, z=0
	:param bank2: point on other bank, z=0
	:param thalweg: thalweg point, z value is missing
	:param x_section: cross sectional area
	:return: depth back calculated using the xsection area and parabola formula
	"""
	# bank1, bank2 are the closest points on the bank with [x, y, 0]'s. X_section is the cross area in m^2
	# want to set thalweg_z which is unknown from using the x-section area and parabola formula's

	total_distance = TwoD_distance(bank1, thalweg) + TwoD_distance(bank2, thalweg)

	#parabola x section area equal to 2/3 * change in height * distance
	#x_section = float(2)/3 * (bank_z - thalweg_z) * total_distance
	thalweg_z = -1 * x_section / total_distance * float(3) / 2

	return thalweg_z


# converts multiple fields with x,y,z data into a single tuple
def pts_2_tuple(x_field, y_field, z_field):
	xyz = (x_field, y_field, z_field)
	return xyz


def thalweg_or_bank(point1, point2):
	#  checks which point has a lower Z value, returns it as thalweg pt, other is bank
	x1, y1, z1, x2, y2, z2 = point1[0], point1[1], point1[2], point2[0], point2[1], point2[2]
	if z2 < z1:
		thalweg = (x2, y2, z2)
		bank = (x1, y1, z1)
	else:
		thalweg = (x1, y1, z1)
		bank = (x2, y2, z2)
	return thalweg, bank


def point_interval(point1, point2):
	"""Interval  to create points based on the distance between the two input points"""
	distance = TwoD_distance(point1, point2)
	if distance < 50:
		increment = 5
	elif distance < 100:
		increment = 10
	elif distance < 500:
		increment = 25
	elif distance < 1000:
		increment = 50
	else:
		increment = 75
	return increment, distance


def gen_pts(thalweg, bank):
	"""Generates points (as tuples) from two input points using the half_parabola_depth function"""
	interval = point_interval(thalweg, bank)
	increment = interval[0]
	distance = interval[1]

	new_points = []

	d_line = 0
	while d_line < distance:
		new_points.append(half_parabola_depth(thalweg, bank, d_line))
		d_line += increment

	return new_points


def width_depth(width_field):
	"""Calculates thalweg depth field from the cross section width between the channel edges. See tech memo #1"""
	depth = -1 * 0.8516 * width_field ** 0.411
	return depth
