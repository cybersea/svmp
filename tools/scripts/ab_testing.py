#from trans2shp import test_csv

#csv_file = "C:\\projects\\dnr_svmp\\input\\VegMon\\2007_Field_Season\\Site Folders\\test001\\test001TD.csv"

#test_csv(csv_file)

#---------------

#from svmpUtils import make_siteList

#sitefile = "C:\\projects\\dnr_svmp\\input\\VegMon\\2007_Field_Season\\Site Folders\\site2process_ab.txt"

#make_siteList(sitefile)

#---------------


#--------------------------------------------------------------------------
#Imports
#--------------------------------------------------------------------------
import sys
import os 
import arcgisscripting 
# Import functions used for SVMP scripts
import svmpUtils as utils
# Import the custom Exception class for handling errors
from svmp_exceptions import SvmpToolsError

def msg(msg):
    gp.AddMessage(msg)

shapefile = "C:/projects/dnr_svmp/output/eelgrass_monitoring/site_folders/nps1446/video_transect_data/2008_nps1446_transect_data.shp"
selStatement = '"tran_num" = 1'

try:

    # Create the geoprocessing object
    gp = arcgisscripting.create()
    # Overwrite existing output data 
    gp.OverWriteOutput = 1

    # Create the custom error class
    # and associate it with the gp
    e = SvmpToolsError(gp)
    # Set some basic defaults for error handling
    e.debug = True
    e.full_tb = True
    #e.exit_clean = False
    #e.pdb = True
    
    msg(selStatement)
    rows = gp.UpdateCursor(shapefile,selStatement)
    row = rows.Next()
    while row:
        id = row.getValue("Id")
        date = row.getValue(utils.shpDateCol)
        msg(id)
        msg(date)
        row = rows.Next()
    del rows



except SystemExit:
    pass
except:
    e.call()
    del gp
