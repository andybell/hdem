#-------------------------------------------------------------------------------
# Name: Raster2ASCII.py	
# Purpose: Converts raster to ASCII
# Author: Andy Bell (ambell@ucdavis.edu) 
# Created: 7/23/2014
#-------------------------------------------------------------------------------
import arcpy, os
from arcpy import env
env.workspace = r"U:\HDEM_v3r1\HDEM_v3r1_Tiles\Tiles"
input = r"U:\HDEM_v3r1\HDEM_v3r1_Tiles\Tiles"
output = r"U:\HDEM_v3r1\HDEM_v3r1_Tiles\Tiles_ASCII"

print env.workspace

rasterList = arcpy.ListRasters("*", "TIF")
print rasterList

for raster in rasterList:
	print "Converting %s to ASCII...." %raster
	base = os.path.basename(raster)
	basename = os.path.splitext(base)[0]
	arcpy.RasterToASCII_conversion (raster, os.path.join(output, basename + ".txt"))
	