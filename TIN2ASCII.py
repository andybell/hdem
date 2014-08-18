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
    arcpy.CheckOutExtension("")

    #get parameters
    tin = arcpy.GetParameterAsText(0)
    output = arcpy.GetParameterAsText(1)
    export_ascii = arcpy.GetParameterAsText(2)

    #tin to raster

    #split raster into chunks

    #chunks into ASCII


except arcpy.ExecuteError:
    print arcpy.GetMessage()
