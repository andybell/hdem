__author__ = 'ambell'

import math

#python parabola formulas for cross section area


def half_parabola(point1, point2):
	#  points are truples that contain (x,y,z)'s
	pass


def cross_section_area(parabola1, parabola2):
	x_area = area(parabola1) + area(parabola2)  # cross section area is the sum of the two parabola curves
	return x_area

point1 = [5,-7,0]
point2 = [3,5,-12]


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

test = ThreeD_distance(point1, point2)
print test

def depth(point1, point2):
	pass