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
import shutil
import zipfile

try:
	#check out arcpy extensions.... if needed
	arcpy.CheckOutExtension("3D")

	#get parameters
	tin = arcpy.GetParameterAsText(0)
	output_folder = arcpy.GetParameterAsText(1)
	rm_temp = arcpy.GetParameterAsText(2)

	sampling = "CELLSIZE 2"
	ntiles = "3 5"  # tile dimensions

	#calculation of total number of tiles desired
	spl = ntiles.split()
	total_tiles = int(float(spl[0]))*int(float(spl[1]))

	#create temporary workspace
	arcpy.AddMessage("Creating temporary folder in %s" % output_folder)
	try:
		os.makedirs(output_folder + "\\raster_tiles")
		r_tiles = os.path.join(output_folder, "raster_tiles")
		os.makedirs(output_folder + "\\ascii_tiles")
		a_tiles = os.path.join(output_folder, "ascii_tiles")
	except:
		arcpy.AddError("Can't make folders... try saving in different location")

	#get tin basename
	base = os.path.basename(tin)
	arcpy.AddMessage("Saving %s as Raster..... " % base)
	TinAsRast = os.path.join(output_folder, base + '.TIF')

	#tin to raster
	arcpy.TinRaster_3d(tin, TinAsRast, 'FLOAT', 'LINEAR', sampling)

	#split raster into chunks
	arcpy.AddMessage("Breaking %s into %s raster tiles....." % (base, total_tiles))
	arcpy.SplitRaster_management(TinAsRast, r_tiles, base + '_',
										'NUMBER_OF_TILES', 'TIFF', 'BILINEAR', ntiles, '#', '10', 'METERS')

	#get list of split tiles
	rastertiles_list = glob.glob(r_tiles + "/*.TIF")
	arcpy.AddMessage(rastertiles_list)

	for raster in rastertiles_list:
		arcpy.AddMessage("Converting %s to ASCII....." % raster)
		rbase = os.path.basename(raster)
		rbaseName, rbaseExt = os.path.splitext(rbase)
		ascii_name = os.path.join(a_tiles, rbaseName + '.txt')
		arcpy.RasterToASCII_conversion(raster, ascii_name)

	#TODO: add option to zip files
	#try using python module zipfile
	if zip_ascii == 'true':
		#get list of ascii tiles
		for ascii in a_tiles:


	# delete temporary scratch folder
	#arcpy.AddMessage(rm_temp)
	if rm_temp == 'true':
		arcpy.AddMessage("Removing Temporary Files....")
		shutil.rmtree(r_tiles)  # removes folder
		arcpy.Delete_management(TinAsRast)  # removes file

except arcpy.ExecuteError:
	print arcpy.GetMessages()
