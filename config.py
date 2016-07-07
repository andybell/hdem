__author__ = 'Andy'

import os

# path that need to be set in order to call R from python

# path to R exe
rscript_path = r"C:\Program Files\R\R-3.2.3\bin\rscript.exe"

# path to R libraries
r_lib_loc = os.path.join(os.path.dirname(__file__), 'Rlib')

