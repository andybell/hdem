# get library paths
path <- .libPaths()

# installs R packages in the first library
library_location <- path[1]

install.packages(c("plyr", "dplyr", "foreign"), lib=library_location)