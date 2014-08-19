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

from arcpy import env
import exceptions, sys, traceback

try:
    #check out arcpy extensions.... if neeeded
    arcpy.CheckOutExtension("3D")

    #get parameters
    tin = arcpy.GetParameterAsText(0)
    output_folder = arcpy.GetParameterAsText(1)
    export_ascii = arcpy.GetParameterAsText(2)

    sampling = "CELLSIZE 2"

    #create temporary workspace
    arcpy.AddMessage("Creating temporary folder in %s" %output_folder)
    try:
        temp = os.makedirs(output_folder + "\\scratch")
        arcpy.env.scratchWorkspace = temp


    #get tin basename
    #base = os.path.basename(tin)
    #arcpy.AddMessage("Test")
    #arcpy.AddMessage(base)

    #tin to raster
    #arcpy.TinRaster_3d(tin, tin_asRaster, "FLOAT", "LINEAR", sampling)

    #split raster into chunks
    #arcpy.SplitRaster_management()

    #chunks into ASCII

    #get list of split tiles

    #for chunk in rastertiles:
        arcpy.RasterToASCII_conversion()


    # delete temporary scratch folder
except arcpy.ExecuteError:
	print arcpy.GetMessages()
