#-------------------------------------------------------------------------------
# Name:        TIN2ASCII.py
# Purpose:      Converts TIN to raster and then splits into ASCII chunks
#
# Author:     Andy Bell
# Contact:    ambell@ucdavis.edu
# Created:     08/18/2014
# Copyright:   (c) ambell 2014
#-------------------------------------------------------------------------------

import arcpy
import os
import glob

from arcpy import env
import exceptions, sys, traceback

try:
    #check out arcpy extensions.... if neeeded
    arcpy.CheckOutExtension("3D")

    #get parameters
    tin = arcpy.GetParameterAsText(0)
    output_folder = arcpy.GetParameterAsText(1)
    rm_temp = arcpy.GetParameterAsText(2)

    sampling = "CELLSIZE 2"
    ntiles = "2 3"  # tile dimensions

    #calculation of total number of tiles desired
    spl = ntiles.split()
    total_tiles = int(float(spl[0]))*int(float(spl[1]))

    #create temporary workspace
    arcpy.AddMessage("Creating temporary folder in %s" %output_folder)
    try:
        os.makedirs(output_folder + "\\raster_tiles")
        r_tiles = os.path.join(output_folder, "raster_tiles")
        os.makedirs(output_folder + "\\ascii_tiles")
        a_tiles = os.path.join(output_folder, "ascii_tiles")
    except:
        arcpy.AddMessage("Can't make folders")

    #get tin basename
    base = os.path.basename(tin)
    arcpy.AddMessage("Saving %s as Raster..... " %base)
    TinAsRast = os.path.join(output_folder, base + ".TIF")

    #tin to raster
    arcpy.AddMessage("Breaking %s into %s raster tiles....." %(base, total_tiles))
    arcpy.TinRaster_3d(tin, TinAsRast, "FLOAT", "LINEAR", sampling)

    #split raster into chunks
    arcpy.SplitRaster_management(TinAsRast, r_tiles, base + "_", "NUMBER_OF_TILES", "TIFF", "BILINEAR", ntiles)

    #get list of split tiles
    rastertiles_list = glob.glob(r_tiles + "/*.TIF")


    for raster in rastertiles_list:
        arcpy.AddMessage("Converting %s to ASCII....." %raster)
        rbase = os.path.basename(raster)
        ascii_name = os.path.join(a_tiles, rbase + ".txt")
        arcpy.RasterToASCII_conversion(raster, ascii_name)

    # delete temporary scratch folder

except arcpy.ExecuteError:
	print arcpy.GetMessages()
