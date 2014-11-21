# near_180 finds two closest points seperated by 180 degrees using a near table gerenated
# using ArcGIS create near table tool. This script should be set up to run using a python
# subproccess module.

#need to change number of digits so XY coordinates don't get cut off
options(scipen=100, digits=18)
require(dplyr)
require(plyr)

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
  limit1 <- neg_angle(first_angle+157.5)
  limit2 <- neg_angle(first_angle+202.5)
  search_180 <- filter(df, if(limit1>limit2){NEAR_ANGLE > limit1 | NEAR_ANGLE < limit2} else{NEAR_ANGLE < limit2 & NEAR_ANGLE > limit1})
  second <-nearest(search_180)
  return(second)
}


####################################################################################

#read in near table from command arguments as near_file
near_file<-"C:\\Users\\ambell.AD3\\Documents\\hdem\\Near_Table_Example_comma.txt"
location<-"C:\\Users\\ambell.AD3\\Documents\\hdem\\export_test.txt"
near_table<-read.csv(near_file, header=TRUE, sep=",")

### use ddply to apply function(s) by IN_FID groups
nearest_vertex<-ddply(near_table, "IN_FID", nearest)
opposite_vertex<-ddply(near_table, "IN_FID", nearest_opposite)

# rm NAs from opposites (no points within the 180 degree search area)
opposite_vertex <-opposite_vertex[complete.cases(opposite_vertex),]

# append files to modifications file
export_bin <-rbind(nearest_vertex, opposite_vertex) # then just append using rbind

#write table out to csv so that python can read it???
write.table(export_bin, location, sep = ",", quote = FALSE, row.names=F)

