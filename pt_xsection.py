__author__ = 'ambell'

# have a point in the middle of the channel
# need to get the two closes banks
# xsection not necessary perpendicular to thalweg
# based on Near180.R
#Do depths matter???? if we just join depths from points latter it would be much much easier since the fields would
# all be consistent

import arcpy
import subprocess
import tempfile
import shutils
import os


#make temp directory to store all interim data steps
dirpath = tempfile.mkdtemp()
print dirpath

# convert near table to dbf since R can't read the gdb table (stupid esri)
arcpy.TableToTable_conversion(table, dirpath, "Near_table.dbf")

#location of R output dbf file
output_dbf = os.path.join(dirpath, "Near180_table.dbf")

#Subprocess call out to R to run Near180.R functions to reduce near table to two closest records

subprocess.call("R --vanilla --args ")



# remove the temporary directory
# shutil.rmtree(dirpath)
