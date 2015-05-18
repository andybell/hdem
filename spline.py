__author__ = 'Andy'

import scipy.interpolate as si
import arcpy
import csv


def get_fields_as_lists(reach_file, rivermile_field, values_field):
    """ function uses a search cursor to read the feature class and return the values if it is in ascending order"""

    print "Getting fields as sorted lists....."

    fields = [rivermile_field, values_field]

    # empty lists to store attribute values
    y_field = []
    x_field = []

    # search cursor to read through the attribute table and append the values to the lists
    with arcpy.da.SearchCursor(reach_file, fields) as cursor:
        for row in cursor:
            x_field.append(int(row[0]))  # makes river mile an integer
            y_field.append(row[1])

    # quick check to make sure that the items in the rivermile_field are sorted in acending order
    if check_sorted(x_field):  # originally check_sorted(x_field) == True
        return x_field, y_field
    else:
        print "Make that the river mile field is sorted"


def check_sorted(list):
    """ returns true if a list is sorted, false if it is out of order"""
    if sorted(list) == list:
        print "Sorted....Check!"
        return True
    else:
        print "Error: file not sorted"
        return False


def spline_thalweg(x, y):
    """ cubic spline using the scipy interpolate univariate function"""

    spl = si.UnivariateSpline(x, y, s=0.3)  # s is the smoothing factor for the spline interpolation

    min_x = 0
    max_x = max(x)

    # empty data dictionary to store the interpolated values from the spline
    spline_dict = {}

    # interpolates values every 10m from the min to max value of x
    for station_pt in range(min_x, max_x, 10):
        spline_value = spl.__call__(station_pt, nu=0)  # uses the UnivariateSpline.__call__ to interpolate a value at x

        # adds spline value to dictionary with station pt value as key
        spline_dict[station_pt] = float(spline_value)

    return spline_dict


def dict2csv(dictionary, export_file):
    """ exports the a data dict to a csv file"""
    with open(export_file, 'wb') as f:
        datawriter = csv.writer(f)
        for key, value in dictionary.iteritems():
            row = key, value
            datawriter.writerow(row)





# tester files

reach_file = r"C:\Users\Andy\Documents\Historical_Delta\Moke_xarea\Reaches\sort\SFMoke.shp"

output = r"C:\Users\Andy\Documents\Historical_Delta\Moke_xarea\Reaches\sort\SFmoke_interp.csv"

print "Getting Values..."
values = get_fields_as_lists(reach_file, "ET_STATION", "AREA")

print "Spline...."
spline = spline_thalweg(values[0], values[1])

print spline

print "Saving to csv...."
dict2csv(spline, output)


print "Done!!!"