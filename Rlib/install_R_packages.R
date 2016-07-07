# installs R packages in the Rlib folder of the toolbox
library_location <- dirname(sys.frame(1)$ofile) # make sure to source

# install packages at the library_location
install.packages('plyr', lib=library_location)
install.packages('dplyr', lib=library_location)
install.packages('foreign', lib=library_location)