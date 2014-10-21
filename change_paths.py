__author__ = 'ambell'

import arcpy
import os

old_path = r"U:\HDEM_v4r2\Tin_Inputs_v4r2.gdb"
new_path = r"U:\HDEM_v4r3\Tin_Inputs_v4r3.gdb"

mxd = arcpy.mapping.MapDocument("CURRENT")

#returns name of layers in current map document and then their workspace paths as dict
def layer_list(map_doc):
	layers = {}
	for lyr in arcpy.mapping.ListLayers(mxd):
		if lyr.supports("DATASOURCE"):
			layers[lyr.name] = lyr.workspacePath
	return layers

#replace old workspace paths with new workspace paths set above
mxd.findAndReplaceWorkspacePaths(old_path, new_path)
mxd.save()