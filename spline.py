__author__ = 'Andy'

import parabola
import scipy
import arcpy
import tempfile




def get_fields_as_lists(reach_file, rivermile_field, values_field):

    #arcpy.Sort_management(reach_file, reach_file, [[rivermile_field, "ASCENDING"]])

    print "Getting fields as sorted lists....."

    fields = [rivermile_field, values_field]

    y_field = []
    x_field = []

    with arcpy.da.SearchCursor(reach_file, fields) as cursor:
        for row in cursor:
            x_field.append(row[0])
            y_field.append(row[1])

    if check_sorted(x_field) == True:
        return x_field, y_field
    else:
        print "Make that the river mile field is sorted"


def check_sorted(list):
    if sorted(list) == list:
        print "Sorted....Check!"
        return True
    else:
        print "Error: file not sorted"
        return False

def spline_thalweg():
    scipy.interpolate.interp1d()
    pass


