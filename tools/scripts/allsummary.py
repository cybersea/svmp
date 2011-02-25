#--------------------------------------------------------------------------
# Tool Name:  AllSitesAnnualSummary
# Tool Label: All Sites Annual Summary
# Source Name: allsummary.py
# Version: ArcGIS 9.2
# Author: Allison Bailey, Sound GIS
# For: Washington DNR, Submerged Vegetation Monitoring Program (SVMP)
# Date: April 2007
# Requires: Python 2.4

# This script outputs four comma-delimited text files
# containg annual summaries of the area and depth sampling
# statistics for both soundwide and focus study sites

# Parameters:
# (1) surveyYear -- Survey Year of interest
# (2) siteTable -- Full path to annual site statistics table
# (3) allsitesFC -- Feature Class containing point locations for all sites
# (4) outAreaSWFileName -- Full path to output file for Soundwide Area stats
# (5) outAreaFocusFileName -- Full path to output file for Focus Area stats
# (6) outDepSWFilename -- Full path to output file for Soundwide Depth stats
# (7) outDepFocusFileName -- Full path to output ifle for Focus Depth stats

#--------------------------------------------------------------------------
#Imports
#--------------------------------------------------------------------------
import sys, os, arcgisscripting 
# Import functions used for SVMP scripts
import svmpUtils
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
# Extract the data from the table using a select statement and column list
def get_siteData(dataTable,colList,siteIDCol,gp):
    # initalize list to hold extracted data
    siteData = {}
    # Search Cursor with the selection statement
    rows = gp.SearchCursor(dataTable)
    row = rows.Next()
    while row:
        # initialize list to hold data for the row
        rowData = []
        # Get the data from each desired column and put in list
        for col in colList:
            rowData.append(row.GetValue(col))
        # Append row data list, to list of lists for all data
        siteData[row.GetValue(siteIDCol)] = rowData
        row = rows.Next()
    del rows
    return siteData
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
# Create two dictionaries with lists of sites by type of
# Soundwide and Focus sites
def siteByType(sites,locData):    
    # print "locData %s" % locData
    # Create a list of empty lists of same length as list of types
    emptyLists = []
    for i in range(len(svmpUtils.sitetypeList)):
        emptyLists.append([])
    
    # Initialize Dictionaries to hold type and list of sites            
    SWsiteDict = dict(zip(svmpUtils.sitetypeList,emptyLists))
    FocsiteDict = dict(zip(svmpUtils.sitetypeList,emptyLists))
    # print SWsiteDict
    # print FocsiteDict
    
    # Get the list of sites that fall into each type
    for site in sites:
        # print "Site %s" % site
        for type in svmpUtils.sitetypeList:
            print type
            # if the site's type matches the current type
            if locData[site][svmpUtils.sitePtCols.index(svmpUtils.siteTypeCol)] == type:
                # if the site's SoundWide Flag is set
                if locData[site][-2]:
                    # print locData[site][-2]
                    SWsiteDict[type] = SWsiteDict[type] + [site]
                # if the sites' Focus site Flag is set
                if locData[site][-1]:
                    FocsiteDict[type] = FocsiteDict[type] + [site]
    return (SWsiteDict,FocsiteDict)
        
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
# Create two dictionaries with site data for Area and Depth output
def siteStats(sites,statsData,locData):   
    AreaSiteDict = {}
    DepSiteDict = {}
    
    for site in sites:
        loc = locData[site][svmpUtils.sitePtCols.index(svmpUtils.siteLocnCol)]
        # print site, loc 
        #--- Values for Area Statistics
        lat = statsData[site][svmpUtils.siteTabCols.index(svmpUtils.approx_latCol)]
        lon = statsData[site][svmpUtils.siteTabCols.index(svmpUtils.approx_lonCol)]
        date = statsData[site][svmpUtils.siteTabCols.index(svmpUtils.samplestartdateCol)]
        numtrans = statsData[site][svmpUtils.siteTabCols.index(svmpUtils.num_transectsCol)]
        zmfraction = statsData[site][svmpUtils.siteTabCols.index(svmpUtils.estmean_zmfractionCol)]
        zmarea = statsData[site][svmpUtils.siteTabCols.index(svmpUtils.est_basalcovCol)] * svmpUtils.sf2_ha
        variance = statsData[site][svmpUtils.siteTabCols.index(svmpUtils.estvar_basalcovCol)] * svmpUtils.sf4_ha2
        cv = statsData[site][svmpUtils.siteTabCols.index(svmpUtils.cv_basalcovCol)]
        
        AreaSiteDict[site] = ",".join((str(site),str(loc),str(lat),str(lon),str(date),\
                             str(numtrans),str(zmfraction),str(zmarea),str(variance),str(cv)))
        
        #-- Values for Depth Statistics
        num_mindep = statsData[site][svmpUtils.siteTabCols.index(svmpUtils.num_minzmdepCol)]
        abs_mindep = statsData[site][svmpUtils.siteTabCols.index(svmpUtils.min_minzmdepCol)] * svmpUtils.f_m
        mean_mindep = statsData[site][svmpUtils.siteTabCols.index(svmpUtils.mean_minzmdepCol)] * svmpUtils.f_m
        se_mindep = statsData[site][svmpUtils.siteTabCols.index(svmpUtils.se_minzmdepCol)]
        num_maxdep = statsData[site][svmpUtils.siteTabCols.index(svmpUtils.num_maxzmdepCol)]
        abs_maxdep = statsData[site][svmpUtils.siteTabCols.index(svmpUtils.max_maxzmdepCol)] * svmpUtils.f_m
        mean_maxdep = statsData[site][svmpUtils.siteTabCols.index(svmpUtils.mean_maxzmdepCol)] * svmpUtils.f_m
        se_maxdep = statsData[site][svmpUtils.siteTabCols.index(svmpUtils.se_maxzmdepCol)]        
        DepSiteDict[site] = ",".join((str(site),str(loc),\
                                    str(num_mindep),str(abs_mindep),str(mean_mindep),str(se_mindep),\
                                    str(num_maxdep),str(abs_maxdep),str(mean_maxdep),str(se_maxdep)))

    return (AreaSiteDict,DepSiteDict)
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
## Create two dictionaries with site data for Area and Depth output
def write_output(siteTypeDict,dataDict,headers,outFileName):  
    
    try:
        outFile = open(outFileName,'w')
        outFile.write(headers)
        
        # Loop through each type of site
        i = 0 # iterator for counting types
        for type in svmpUtils.sitetypeList:
            # See if there are any sites of that type
            sites = siteTypeDict[type]
            if sites:
                # Write the Type header for this group of sites
                # If it's not the first category, add an extra blank line
                if i:
                    outFile.write("\n")
                outFile.write(svmpUtils.sitetypeDict[type] + "\n")
                i = i + 1
                # Loop through all sites of that type
                for site in sites:
                    # Write out the data for the site
                    outFile.write(dataDict[site] + "\n")
                
        outFile.close()
        
    except:
        outFile.close()
        gp.AddError("Problem writing output file:" + outFileName) 
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
        # Survey Year for data to be processed
        surveyYear = gp.GetParameterAsText(0) 
        # Full Path to annual site statistics table
        siteTable = gp.GetParameterAsText(1) 
        # Feature Class containing point locations for all sites
        allsitesFC = gp.GetParameterAsText(2)           
        # Full path to output file for Soundwide Area stats
        outAreaSWFileName = gp.GetParameterAsText(3)
        # Full path to output file for Focus Area stats
        outAreaFocusFileName = gp.GetParameterAsText(4)
        # Full path to output file for Soundwide Depth stats
        outDepSWFileName = gp.GetParameterAsText(5)
        # Full path to output file for Focus Depth stats
        outDepFocusFileName = gp.GetParameterAsText(6)

        # print "Got the parameters"
                
        # Get a dictionary of sites and data from the sites table
        siteStatsData = get_siteData(siteTable,svmpUtils.siteTabCols,svmpUtils.siteCol,gp)

        # Column names for soundwide and focus site flags
        swCol = 'Y' + str(surveyYear)
        focusCol = swCol + 'focus'
        
        # Append these two to the other data columns needed for location info
        siteLocCols = svmpUtils.sitePtCols
        siteLocCols.append(swCol)
        siteLocCols.append(focusCol)
        
        # Get a dictionary of sites and data from the location table
        siteLocData = get_siteData(allsitesFC,siteLocCols,svmpUtils.sitePtIDCol,gp)
        
        # Sorted Site list
        siteList = siteStatsData.keys()
        siteList.sort()        
        
        # Create Dictionaries with lists of sites by Type for
        # Soundwide and Focus Sites
        # print "Creating Dictionaries of sites by type"
        (SWsiteDict,FocsiteDict) = siteByType(siteList,siteLocData)
        
        # Assemble Data for Area Statistics and Depth Statistics
        # print "Assemble data"
        (AreaSiteDict,DepSiteDict) = siteStats(siteList,siteStatsData,siteLocData)
        
        # Area Stats Summary Header Rows
        AreaHeaders = ",,,,,,Z. marina,Z. marina,,\n" + \
            ",,Approximate,Approximate,,Number,Fraction,Area,,Coefficient\n" + \
            ",,Latitude,Longitude,Date ,of,Along,at Site,,of\n" + \
            "Site,Location,(decimal degrees),(decimal degrees),Sampled,Transects,Transects,(hectares),Variance,Variation\n"
        
        # Depth Stats Summary Header Rows
        DepthHeaders = ",,,,Minimum Z. marina Depth,,,,Maximum Z. marina Depth\n" + \
                        ",,,Absolute,Mean,Standard,,Absolute,Mean,Standard\n" + \
                        "Site,Location,n,Depth (m),Depth (m),Error,n,Depth (m),Depth (m),Error\n" 
    
        
        # Soundwide Area output
        gp.AddMessage("Creating output file: " + outAreaSWFileName)
        write_output(SWsiteDict,AreaSiteDict,AreaHeaders,outAreaSWFileName)
        # Focus Site Area output
        gp.AddMessage("Creating output file: " + outAreaFocusFileName)
        write_output(FocsiteDict,AreaSiteDict,AreaHeaders,outAreaFocusFileName)
        # Soundwide Depth output
        gp.AddMessage("Creating output file: " + outDepSWFileName)
        write_output(SWsiteDict,DepSiteDict,DepthHeaders,outDepSWFileName)
        # Focus site Depth output
        gp.AddMessage("Creating output file: " + outDepFocusFileName)
        write_output(FocsiteDict,DepSiteDict,DepthHeaders,outDepFocusFileName)

    except:
        print sys.exc_info()
        print gp.GetMessages()
        gp.AddError("An error occurred in AllSitesAnnualSummary")
        del gp  
        
  
