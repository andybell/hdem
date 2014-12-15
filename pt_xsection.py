__author__ = 'ambell'

# have a point in the middle of the channel
# need to get the two closest banks
# xsection not necessary perpendicular to thalweg
# based on Near180.R
# Do depths matter???? if we just join depths from points latter it would be much much easier since the fields would
# all be consistent

import arcpy
import subprocess
import tempfile
import shutil
import os

"""#make temp directory to store all interim data steps
dirpath = tempfile.mkdtemp()

# convert near table to dbf since R can't read the gdb table (stupid esri)
arcpy.TableToTable_conversion(table, dirpath, "Input_Near_table.dbf")

#location of R output dbf file
input_dbf = os.path.join(dirpath, "Input_Near_Table.dbf")
near180 = r"C:\Users\ambell.AD3\Documents\hdem\R_HDEM\Near180.R" # TODO change to be universal?
rscript_path = r"C:\Users\ambell.AD3\Documents\R\R-3.1.2\bin\rscript.exe" # TODO universal?


print "Calling {} {} --args {} {}".format(rscript_path, near180, input_dbf, dirpath)
#Subprocess call out to R to run Near180.R functions to reduce near table to two closest records
subprocess.call([rscript_path, near180, "--args", input_dbf, dirpath])


#TODO add field for join (THALWEG_Z and BANK_Z as doubles)
def addfields(target_table, name_list):
	for name in name_list:
		arcpy.AddField_management(target_table, name, "DOUBLE")

new_fields = ["THALWEG_Z", "BANK_Z"]

addfields(os.path.join(dirpath, "nearest_bank.dbf"), new_fields)
addfields(os.path.join(dirpath, "opposite_bank.dbf"), new_fields)

# remove the temporary directory
# shutil.rmtree(dirpath)
"""

# TODO delete file, code has been migrated to gen_parabolas.py