#-------------------------------------------------------------------------------
# Name:        TIN_display.py
# Purpose:      Creates a TIN from current display extent
#
# Author:     Andy Bell
# Contact:    ambell@ucdavis.edu
# Created:     08/19/2014
# Copyright:   (c) ambell 2014
#-------------------------------------------------------------------------------

import arcpy
import exceptions, sys, traceback
import arcpy.mapping
from arcpy import env

try:
    arcpy.CheckOutExtension("3D")

    #output from parameter
    output = arcpy.GetParameterAsText(0)

    # TIN inputs
    TINputs = "Bathymetry/channel_double NAVD88_m Mass_Points <None>;Bathymetry/H00935_t2r_10m NAVD88_m Mass_Points <None>;Bathymetry/manual_pts NAVD88_m Mass_Points <None>;Bathymetry/Small_parabolas_full NAVD88_m Mass_Points <None>;Bathymetry/Channel_edges_dice NAVD88_m Hard_Line <None>;Bathymetry/channel_lines_dice NAVD88_m Hard_Line <None>;Crests_NAVD88 Elevation_NAVD88_m Hard_Line <None>;Levee_Foots_erase_30m_dice Z_Mean Hard_Line <None>"
    proj = "PROJCS['NAD_1983_UTM_Zone_10N',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-123.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]"


    #TIN symbology
    symb = "U:/HDEM_v3r2/TINs/HDEM_SNs.lyr"


    #Get display extent from layout view (not sure if there is a better way since data view extent depends on the size of arcmap window)

    IMXD = arcpy.mapping.MapDocument("Current") # set current mxd

    DF = arcpy.mapping.ListDataFrames(IMXD)[0] # Set Dataframe

    display = DF.extent #display extent

    arcpy.env.extent = display #set's the env extent to match the display extent. Not sure if tool with respect values!


    #Create TIN
    arcpy.CreateTin_3d(output, proj, TINputs, "DELAUNAY")


    # Add output to map with correct symbology
    try:
        arcpy.env.addOutputsToMap(True)
        arcpy.ApplySymbologyFromLayer_management(output, symb)
    except:
        arcpy.AddMessage("Unable to add in TIN automatically.")

except arcpy.ExecuteError:
	print arcpy.GetMessages()



