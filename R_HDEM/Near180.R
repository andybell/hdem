# near_180 finds two closest points seperated by 180 degrees using a near table gerenated
# using ArcGIS create near table tool. This script should be set up to run using a python
# subproccess module.

require(foreign)
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
  limit1 <- neg_angle(first_angle+135)
  limit2 <- neg_angle(first_angle+225)
  search_180 <- filter(df, if(limit1>limit2){NEAR_ANGLE > limit1 | NEAR_ANGLE < limit2} else{NEAR_ANGLE < limit2 & NEAR_ANGLE > limit1})
  second <-nearest(search_180)
  return(second)
}


# writes out df to a table. IDL needs comma seperated but saved as a .txt file 
export_table <- function(df){
  write.table(df, file = file.choose(), sep = ",", quote = FALSE, row.names=F)
}

# add zeros for Z2 -- waterline at MLLW
add_z2 <- function(df){
  df["Z2"]<-0
  df
}

# drops unneccessary fields from the files and reorgizes them correctly
# only want to keep OBJECTID, X1, Y1, Z1, X2, Y2, Z2
drop_fields <- function(df){
  fields = c("OBJECTID", "X1", "Y1", "Z1", "X2", "Y2", "Z2")
  df <- subset(df, select = fields)
}


# read dbf file in list of files
nears<-read.dbf(files[i])

# add column for Z2
add_z2(nears)->nears


### use ddply to apply function(s) by IN_FID groups
nearest_vertex<-ddply(nears, "IN_FID", nearest)
opposite_vertex<-ddply(nears, "IN_FID", nearest_opposite)

# rm NAs from opposites (no points within the 180 degree search area)
opposite_vertex <-opposite_vertex[complete.cases(opposite_vertex),]

#drop all unnecessary fields from nearest_vertex and opposite vertex dframes

drop_fields(nearest_vertex)->nearest_vertex
drop_fields(opposite_vertex)->opposite_vertex

# append files to modifications file
modifications_bin <-rbind(modifications_bin, nearest_vertex, opposite_vertex) # then just append using rbind to mod_bin