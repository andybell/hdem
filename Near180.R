# Near180.R finds the two closest points seperated by ~180 degrees using a table generated
# using ArcGIS's Create Near Table tool. This script should be set up to run using a python
# subproccess module.

#change number of digits so XY coordinates don't get cut off
options(scipen=100, digits=18)

####################################################################################

#read in near table from command arguments as near_file
args <- commandArgs(trailingOnly=TRUE)
near_file<-args[2]
out_location<-args[3]
bind<-args[4]
library_location <- args[5]
print(args)


####################################################################################

#set lib.loc file path in config.py
library('plyr', lib.loc = library_location)
library('dplyr', lib.loc = library_location)
library('foreign', lib.loc = library_location)
library('lazyeval', lib.loc = library_location)

# change arc's angles  with 0 = due east
neg_angle<-function(angle){
  angle360<-angle%%360
  if (angle360 <= 180){angle360}
  else{angle360%%-180}}

# find the row with the minimum near_distance
nearest <- function(df){
  minima_row <- min(which(df$NEAR_DIST == min(df$NEAR_DIST)))
  return (df[minima_row,])
}

# find the row that has the lowest near distance opposite from the closest point
nearest_opposite <- function(df){
  first<-nearest(df)
  first_angle <- first[1, "NEAR_ANGLE"]
  limit1 <- neg_angle(first_angle+135) #changed from 157.5
  limit2 <- neg_angle(first_angle+225) # changed from 202.5
  search_180 <- filter(df, if(limit1>limit2){NEAR_ANGLE > limit1 | NEAR_ANGLE < limit2} else{NEAR_ANGLE < limit2 & NEAR_ANGLE > limit1})
  second <-nearest(search_180)
  return(second)
}

####################################################################################

# read dbf file as a table
near_table<-read.dbf(near_file, as.is = FALSE)

# use ddply to apply function(s) by IN_FID groups
nearest_point<-ddply(near_table, "IN_FID", nearest)
print("Nearest Finished")
print("Nearest Finished")
print("Nearest Finished")
print("Nearest Finished")
print("Nearest Finished")
print("Nearest Finished")
print("Nearest Finished")

opposite_point<-ddply(near_table, "IN_FID", nearest_opposite)
print("Opposite Finished")

# rm NAs from opposites (no points within the 180 degree search area)
opposite_point <-opposite_point[complete.cases(opposite_point),]

# write tables out to dbf so that python can read it
print("Saving near points as a DBFs in temp directory")

# bind parameter for output. Opposite bank are either appended or merged/joined to nearest bank points
if(bind=="APPEND"){
# append files to modifications file
export_bin <-rbind(nearest_point, opposite_point) # then just append using rbind

# write table out to dbf so that python can read it
write.dbf(export_bin, paste(out_location, "both_banks.dbf", sep="\\"))

}else if (bind=="MERGE"){

# join/merge nearest and opposite banks on unique FID
merged<-merge(nearest_point, opposite_point, by = "IN_FID")

# fields to keep from the join
keeps<-c("IN_FID", "FROM_X.x", "FROM_Y.x", "NEAR_X.x", "NEAR_Y.x", "NEAR_X.y", "NEAR_Y.y")
banks<-merged[keeps]

# rename columns
new_names <-c("IN_FID", "T_X", "T_Y", "B1_X", "B1_Y", "B2_X", "B2_Y")
colnames(banks)<-new_names

# write out result to dbf file
write.dbf(banks, paste(out_location, "both_banks_join.dbf", sep="\\"))
}
