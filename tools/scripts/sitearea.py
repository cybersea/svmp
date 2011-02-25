#--------------------------------------------------------------------------
# Tool Name:  SingleSiteAreaSummary
# Tool Label: Single Site Area Summary
# Source Name: sitearea.py
# Version: ArcGIS 9.2
# Author: Allison Bailey, Sound GIS
# For: Washington DNR, Submerged Vegetation Monitoring Program (SVMP)
# Date: April 2007, modified June2007
# Requires: Python 2.4

# This script outputs a comma-delimited text file
# Containg a summary of the length and area sampling results
# for all transects at a single site

# Parameters:
# (1) siteID -- Identifier for the site of interest
# (2) surveyYear -- Survey Year of interest
# (3) siteTable -- Full path to annual site statistics table
# (4) transTable -- Full path to annual transect statistics table
# (5) outFileName -- Full path to output summary data file

#--------------------------------------------------------------------------
#Imports
#--------------------------------------------------------------------------
import sys, os, arcgisscripting 
# Import functions used for SVMP scripts
import svmpUtils
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
# Calculate sum of a particular column from a list of lists
def calc_Totals(i,dataList):
    total = 0
    for d in dataList:
        total = total + d[i]
        
    return total

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
        
        # Get Transect statistics from the database:

        # Header Text
        headLn1 = ',,,Washington State Department of Natural Resources,,\n' 
        headLn2 = ',,,Submerged Vegetation Monitoring Project,,\n'
        headLn3 = ',,,' + surveyYear + ' Field Survey,,\n'
        headLn4 = ',,,Z. marina area based on ' + surveyYear + ' sample area,,\n'
        headLn5 = ',,,Site: ' + siteID + ',,\n'
        headLn6 = ',,,,,\n'
        headLn7 = ',,,Transect Sampling Results,,\n'
        headLn8 = '\n'
        headerText = headLn1 + headLn2 + headLn3 + headLn4 + headLn5 + headLn6 + headLn7 + headLn8
        
        # Column Headers
        columnHeaderText = ',Transect,Date,Sample Length (ft),Eelgrass Length (ft),Eelgrass Fraction\n'
        print columnHeaderText
        
        # SQL select statement to extract data records for the site of interest
        selStatement = '[' + svmpUtils.siteCol + ']' + ' = ' + '\"' + siteID + '\"'

        # Get Transect statistics from the database
        # List of columns, in order, to get data for transect depth
        transColList = [svmpUtils.trkCol,svmpUtils.trandateCol,svmpUtils.samplenCol,
                        svmpUtils.zmlenCol,svmpUtils.zmfractionCol] 
        transData = svmpUtils.get_Data(transTable,selStatement,transColList,gp)
        
        # Sums of various columns
        totSampLen = calc_Totals(2,transData)
        totZMLen = calc_Totals(3,transData)
        
        # Get Site statistics from the database
        # List of columns, in order, to get data for site depth stats
        siteColList = [svmpUtils.estmean_zmfractionCol, svmpUtils.estvar_zmfractionCol,
                        svmpUtils.samp_areaCol,svmpUtils.est_basalcovCol,
                        svmpUtils.estvar_basalcovCol]
        siteData = svmpUtils.get_Data(siteTable,selStatement,siteColList,gp)
        
        # Check to see if there is data returned from the SQL query
        # If no data returned, tell the user and bail out with an exception
        if siteData:
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
            for t in transData:
                transString = "," + ",".join([str(d) for d in t]) + "\n"
                outFile.write(transString)
            # Totals row
            outFile.write('Totals,,,' + str(totSampLen) + ',' + str(totZMLen) + ',,,,')
            # Write a few empty rows
            outFile.write('\n\n\n')
            # Write the depth data for the site
            for s in siteData:
                # mean eelgrass fraction
                outFile.write('Estimated mean eelgrass fraction:,,,,' + str(s[0]) + '\n')
                # variance of eelgrass fraction
                outFile.write('Estimated variance of eelgrass fraction:,,,,' + str(s[1]) + '\n\n')
                # sample area
                outFile.write('Total sample area within perimeter (sq ft):,,,,' + str(s[2]) + '\n')
                # basal area coverage
                outFile.write('Estimated basal area coverage (sq ft): ,,,,' + str(s[3]) + '\n')
                # variance of basal area coverage
                outFile.write('Estimated variance of basal area coverage (ft ^ 4): ,,,,' + str(s[4]) + '\n')
        finally:
            outFile.close()  
                        
        outFile.close()         
                

    except:
        print sys.exc_info()
        print gp.GetMessages()
        gp.AddError("An error occurred in SingleSiteDepthSummary")
        del gp  
        
