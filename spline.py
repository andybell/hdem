__author__ = 'Andy'

import scipy.interpolate as si
import arcpy
import csv


def get_fields_as_lists(reach_file, rivermile_field, values_field):
    # arcpy.Sort_management(reach_file, reach_file, [[rivermile_field, "ASCENDING"]])

    print "Getting fields as sorted lists....."

    fields = [rivermile_field, values_field]

    y_field = []
    x_field = []

    with arcpy.da.SearchCursor(reach_file, fields) as cursor:
        for row in cursor:
            x_field.append(int(row[0])) # makes river mile an integer
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


def spline_thalweg(x, y):
    spl = si.UnivariateSpline(x, y, s=0.3)

    min_x = 0
    max_x = max(x)

    spline_dict = {}

    for station_pt in range(min_x, max_x, 10):
        spline_value = spl.__call__(station_pt, nu=0)

        # adds spline value to dictionary with station pt value as key
        spline_dict[station_pt] = float(spline_value)

    return spline_dict


def dict2csv(dictionary, export_file):
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