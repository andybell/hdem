__author__ = 'ambell'

import arcpy
import os

old_path = r"U:\HDEM_v4r3_102214\Tin_Inputs_v4r3.gdb"
new_path = r"U:\HDEM_v4r4\Tin_Inputs_v4r4.gdb"

mxd = arcpy.mapping.MapDocument("CURRENT")

#returns name of layers in current map document and then their workspace paths as dict
def layer_list(map_doc):
	layers = {}
	for lyr in arcpy.mapping.ListLayers(map_doc):
		if lyr.supports("DATASOURCE"):
			layers[lyr.name] = lyr.workspacePath
	return layers

#replace old workspace paths with new workspace paths set above
mxd.findAndReplaceWorkspacePaths(old_path, new_path)
mxd.saveACopy(r"U:\HDEM_v4r4\HDEM_v4r4_copy")