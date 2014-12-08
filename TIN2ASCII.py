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
import make_zip
#import file_size #removed all code that requires module

try:
	#check out arcpy extensions.... if needed
	arcpy.CheckOutExtension("3D")

	#get parameters
	tin = arcpy.GetParameterAsText(0)
	output_folder = arcpy.GetParameterAsText(1)
	zip_ascii = arcpy.GetParameterAsText(2) #TODO: remove required from arcgis tool interface. it should be optional.
	rm_temp = arcpy.GetParameterAsText(3)

	sampling = "CELLSIZE 2"
	ntiles = "3 5"  # tile dimensions # TODO: increase the number of tiles to that Suisun is included

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
	#arcpy.AddMessage(rastertiles_list)

	for raster in rastertiles_list:
		arcpy.AddMessage("Converting %s to ASCII....." % raster)
		rbase = os.path.basename(raster)
		rbaseName, rbaseExt = os.path.splitext(rbase)
		ascii_name = os.path.join(a_tiles, rbaseName + '.txt')
		arcpy.RasterToASCII_conversion(raster, ascii_name)

	#zips files using make_zip.py and calculates amount of compression
	if zip_ascii == 'true':
		arcpy.AddMessage("Zipping ASCII files...")
		zipped_output = os.path.join(output_folder, base + "_ascii_tiles.zip")
		make_zip.zip_folder(a_tiles, zipped_output)

		#get size not working and it is not needed
		#unzipped_size = file_size.get_size(a_tiles) * 0.000000001
		#zipped_size = file_size.get_size(zipped_output) * 0.000000001 # TODO: this is not working. File size = 0
		#arcpy.AddMessage("Original size: %s GB    Compressed size: %s GB" % (unzipped_size, zipped_size))

	# delete temporary scratch folder
	#arcpy.AddMessage(rm_temp)
	if rm_temp == 'true':
		arcpy.AddMessage("Removing Temporary Files....")
		shutil.rmtree(r_tiles)  # removes folder
		shutil.rmtree(a_tiles)
		arcpy.Delete_management(TinAsRast)  # removes file

except arcpy.ExecuteError:
	print arcpy.GetMessages()
