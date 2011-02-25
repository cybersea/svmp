#--------------------------------------------------------------------------
# Tool Name:  SingleSiteDepthSummary
# Tool Label: Single Site Depth Summary
# Source Name: sitedep.py
# Version: ArcGIS 9.2
# Author: Allison Bailey, Sound GIS
# For: Washington DNR, Submerged Vegetation Monitoring Program (SVMP)
# Date: April 2007, modified June 2007
# Requires: Python 2.4

# This script outputs a comma-delimited text file
# Containg a summary of the depth sampling results
# for all transects at a single site

# Parameters:
# (1) siteID -- Identifier for the site of interest
# (2) surveyYear -- Survey Year of interest
# (3) siteTable -- Full path to annual site statistics table
# (4) transTable -- Full path to annual transect statistics table
# (4) outFileName -- Full path to output summary data file

#--------------------------------------------------------------------------
#Imports
#--------------------------------------------------------------------------
import sys, os, arcgisscripting 
# Import functions used for SVMP scripts
import svmpUtils
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------

#MAIN

if __name__ == "__main__":

    try:

        # Create the geoprocessing object
        gp = arcgisscripting.create()
        # Overwrite existing output data 
        gp.OverWriteOutput = 1

        #Get parameters
        # The identifier for the site of interest
        siteID = gp.GetParameterAsText(0)  
        # Survey Year for data to be processed
        surveyYear = gp.GetParameterAsText(1) 
        # Full Path to annual site statistics table
        siteTable = gp.GetParameterAsText(2) 
        # Full Path to annual transect statistics table
        transTable = gp.GetParameterAsText(3)           
        # Full path to output text file
        outFileName = gp.GetParameterAsText(4)
        
        # Header Text
        headLn1 = ',,Washington State Department of Natural Resources,,,\n' 
        headLn2 = ',,Submerged Vegetation Monitoring Project,,,\n'
        headLn3 = ',,' + surveyYear + ' Field Survey,,,\n'
        headLn4 = ',,Site: ' + siteID + ',,,\n'
        headLn5 = ',,,,,\n'
        headLn6 = ',,Eelgrass BioSonics Depth Sampling Results,,,\n'
        headLn7 = '\n'
        headerText = headLn1 + headLn2 + headLn3 + headLn4 + headLn5 + headLn6 + headLn7
        
        # Column Headers
        columnHeaderText = 'Transect,Date,Max Track Depth (ft),Max Eelgrass Depth (ft),Min Eelgrass Depth (ft),Min Track Depth (ft)\n'
        
        # SQL select statement to extract data records for the site of interest
        selStatement = '[' + svmpUtils.siteCol + ']' + ' = ' + '\"' + siteID + '\"'
        
        # Get Transect statistics from the database
        # List of columns, in order, to get data for transect depth
        transColList = [svmpUtils.trkCol,svmpUtils.trandateCol,svmpUtils.trkmaxdepCol,
                        svmpUtils.zmmaxdepCol,svmpUtils.zmmindepCol, svmpUtils.trkmindepCol] 
        transDepData = svmpUtils.get_Data(transTable,selStatement,transColList,gp)
        
        # Get Site statistics from the database
        # List of columns, in order, to get data for site depth stats
        siteColList = [svmpUtils.num_maxzmdepCol, svmpUtils.num_minzmdepCol,\
                        svmpUtils.min_maxzmdepCol,svmpUtils.min_minzmdepCol,\
                        svmpUtils.max_maxzmdepCol,svmpUtils.max_minzmdepCol,\
                        svmpUtils.mean_maxzmdepCol,svmpUtils.mean_minzmdepCol,\
                        svmpUtils.std_maxzmdepCol,svmpUtils.std_minzmdepCol,\
                        svmpUtils.se_maxzmdepCol,svmpUtils.se_minzmdepCol]
        siteDepData = svmpUtils.get_Data(siteTable,selStatement,siteColList,gp)
        
        # Check to see if there is data returned from the SQL query
        # If no data returned, tell the user and bail out with an exception
        if siteDepData:
            pass
        else:
            gp.AddError("No data for site: " + siteID + " in " + surveyYear)
            raise # send to error handler
        
        # Open the file for output
        outFile = open(outFileName,'w')
        
        # Write the info to the output file
        try:
            # Write the file and column Headers
            outFile.write(headerText + columnHeaderText) 
            # Write the depth data for each transect at the site
            for t in transDepData:
                transString = ",".join([str(d) for d in t]) + "\n"
                outFile.write(transString)
            # Write a few empty rows
            outFile.write(',,,,,\n,,,,,\n\n')
            # Write the depth data for the site
            for s in siteDepData:
                # Number of transects for depth stats
                outFile.write(',n,,' + ",".join([str(d) for d in s[0:2]]) + '\n')
                # Min depths
                outFile.write(',min,,' + ",".join([str(d) for d in s[2:4]]) + '\n')
                # Max depths
                outFile.write(',max,,' + ",".join([str(d) for d in s[4:6]]) + '\n')
                # Mean depths
                outFile.write(',mean,,' + ",".join([str(d) for d in s[6:8]]) + '\n')
                # Standard Deviation of depths
                outFile.write(',st dev,,' + ",".join([str(d) for d in s[8:10]]) + '\n')
                # Standard Error of depths
                outFile.write(',st error,,' + ",".join([str(d) for d in s[10:12]]) + '\n')
        finally:
            outFile.close()  
            
        outFile.close()         

    except:
        print sys.exc_info()
        print gp.GetMessages()
        gp.AddError("An error occurred in SingleSiteDepthSummary")
        del gp  
