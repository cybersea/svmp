import os
import sys
import traceback
import arcgisscripting
from svmp_exceptions import SvmpToolsError

DEBUG = True
PDB_DEBUG = False

# Create the geoprocessing object
gp = arcgisscripting.create()

# Create the custom error class
# and associate it with the gp
error = SvmpToolsError(gp)

# Set some basic defaults for error handling
error.debug = True
error.pdb = True

def main():
  try:
    raise RuntimeError
  except Exception, E:
    error.call('An intentional RuntimeError occurred in the python script..')

if __name__ == "__main__":
  try:
    main()
  except Exception, E:
    error.call(E)

