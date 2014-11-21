__author__ = 'ambell'

# have a point in the middle of the channel
# need to get the two closes banks
# xsection not necessary perpendicular to thalweg
# based on Near180.R


#Asssume we have a near table that contains the nearest points on each of the two banks

#point 1 is the point that has the shortest distance

#make system call to R? and use the same functions? use subproccess?

#Do depths matter???? if we just join depths from points latter it would be much much easier since the fields would
# all be consistent



import arcpy
import subproccess

# convert near table to dbf? or txt file since R can't read the gdb table (stupid esri)

n