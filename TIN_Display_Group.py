#-------------------------------------------------------------------------------
# Name:        TIN_display.py
# Purpose:      Creates a TIN from current display extent
# Notes:        Files are currently hard linked (mxd - HDEM_v3r2_land.mxd)
# Author:     Andy Bell
# Contact:    ambell@ucdavis.edu
# Created:     08/19/2014
# Copyright:   (c) ambell 2014
#-------------------------------------------------------------------------------

import arcpy
import exceptions, sys, traceback
import os
import arcpy.mapping
from arcpy import env

#check fieldnames match_field input
def check_z(fc):
    fieldList = arcpy.ListFields(fc)
    check = False
    for field in fieldList:
        if field.name == z_field:
            check = True
    return check


try:
    arcpy.CheckOutExtension("3D")

    #output from parameter
    output = arcpy.GetParameterAsText(0)
    tin_in_group = arcpy.GetParameterAsText(1)
    z_field = arcpy.GetParameterAsText(2)

    base = os.path.basename(output)
    arcpy.AddMessage(base)

    # TIN inputs
    TINputs = "Bathymetry/channel_double NAVD88_m Mass_Points <None>;Bathymetry/H00935_t2r_10m NAVD88_m Mass_Points <None>;Bathymetry/manual_pts NAVD88_m Mass_Points <None>;Bathymetry/Small_parabolas_full NAVD88_m Mass_Points <None>;Bathymetry/Channel_edges_dice NAVD88_m Hard_Line <None>;Bathymetry/channel_lines_dice NAVD88_m Hard_Line <None>;Levees/Levee_Crests_NAVD88 Elevation_NAVD88_m Hard_Line <None>;Levees/Levee_footprints_split MSL_NAVD88 Hard_Line <None>"
    proj = "PROJCS['NAD_1983_UTM_Zone_10N',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-123.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]"


    #Get display extent from layout view (not sure if there is a better way since data view extent depends on the size of arcmap window)

    IMXD = arcpy.mapping.MapDocument("Current") # set current mxd

    DF = arcpy.mapping.ListDataFrames(IMXD)[0] # Set Dataframe

    display = DF.extent #display extent

    arcpy.env.extent = display #set's the env extent to match the display extent. Not sure if tool with respect values!


    #Get list of TIN input layers
    tinputs = {} # create empty data dictionary

    for layer in arcpy.mapping.ListLayers(IMXD): #not needed
        if layer.name == tin_in_group: # change this to for layer in tin_in_group
            arcpy.AddMessage("TIN inputs: ")
            for subLayer in layer:
                arcpy.AddMessage(subLayer)
                if check_z(subLayer) == True:
                    if arcpy.Describe(subLayer).shapeType == "Point":
                        tinputs[subLayer.name] = "Mass_Points"
                    elif arcpy.Describe(subLayer).shapeType == "Polyline":
                        tinputs[subLayer.name] = "Hard_Line"
                else:
                    arcpy.AddError("Layer does not have a field named %s" %z_field)

    # build Tin input format ("Group_Name/file_name z_field Type <None>;")
    Tin_input_strings = []

    for feature in tinputs:
        feature_str = tin_in_group + "/" + feature + " " + z_field + " " + tinputs[feature] + " " + "<None>"
        #arcpy.AddMessage(feature_str)
        Tin_input_strings.append(feature_str)

    Tin_input_str = ";".join(Tin_input_strings) # joins all individual strings together seperated by semicolon


    #Create TIN
    arcpy.CreateTin_3d(output, proj, Tin_input_str, "DELAUNAY")

except arcpy.ExecuteError:
	print arcpy.GetMessages()




