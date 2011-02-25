""" Calculates annual Soundwide Zostera marina area estimates """

""" 
Tool Name:  SWAreaEstimates
Tool Label: SW Area Estimates
Source Name: sw_area_estimates.py
Version: ArcGIS 9.2
Author: Allison Bailey, Sound GIS
For: Washington DNR, Submerged Vegetation Monitoring Program (SVMP)
Date: December 2009
Requires: Python 2.4

This script calculates soundwide Zostera marina area estimates
for a single survey year.

# Parameters:
(1) siteStatsTable -- Site statistics geodatabase table
(2) allsitesFC -- Feature Class containing point locations for all sites
(3) flatsFC -- ArcGIS feature class for flats sites
(4) fringeFC -- ArcGIS feature class for flats sites
(5) surveyYear -- Survey year for data to be processed

"""

import sys
import arcgisscripting
import svmp 
import svmp_spatial as spatial
import svmpUtils as utils
from svmp_exceptions import SvmpToolsError
from profiling import profileit

# ----------- PARAMETERS ----------------------------------
# Temporary stand-ins for parameters
sitestats_tbl = "svmp_sitesdb_lf.mdb/2007sites"
svmp_all_sites_fc = "svmp_all_sites_041309_samptype.shp"
flats_fc = "flats.shp"
fringe_fc = "fringe.shp"
survey_year = 2007
sample_group = "soundwide"   # placeholder -- may be implemented as a parameter later (for soundwide, focus and other sites)
outfilename_stratum = "%s_swarea_stratum.csv" % (survey_year)
outfilename_all = "%s_swarea_all.csv" % (survey_year)

#-------------- FUNCTIONS ---------------------------------
# Function for inverting a dictionary
def invert_dict(dict):
    inverse = {}
    for (key, value) in dict.items():
        if value not in inverse:
            inverse[value] = []
        inverse[value].append(key)
    return inverse

# Get List of Site data, corresponding to the specified extrapolation type
def group_data_by_extrap(extrap_site_dict,extrap,site_stats_dict):
    # get list of sites for the specified analysis stratum and extrapolation
    site_list = extrap_site_dict[extrap]
    
    # Extract the specified site data from the site statistics dictionary
    dat = []    
    for s in site_list:
        vals = site_stats_dict[s]
        dat.append(vals)
        
    return dat
#------------------------------------------------------------

#---- Create the Geoprocessing Object ----------------------
gp = arcgisscripting.create()

#----- Create the Custom Error Object ----------------------
e = SvmpToolsError(gp)
# Set some basic defaults for error handling
e.debug = True
e.full_tb = True


#----- Get  site list and strata from svmp_all_sites feature class
#---------------------------------------------------------------------------

samp_type_field = "Y%sSAMP" % survey_year

if sample_group == "soundwide":
    #-------------- Construct Query: Soundwide sites for the specified year ---
    samp_type_qry = "%s in ('sw','sw_focus','sw_other')" % samp_type_field

# Query the All Sites feature class
#@profileit(3)
def site_query():
    return spatial.TableQuery(gp,svmp_all_sites_fc,samp_type_qry)

site_characteristics = site_query()

#----- Query All Sites Table for geomorph stratum, and sampling stratum with siteid as key
#@profileit(3)
def site_characteristics_query():
    flds_c = [utils.siteGeoStratCol,utils.siteSampStratCol]
    return site_characteristics.field_results(flds_c,utils.sitePtIDCol)
    
site_characteristics_data = site_characteristics_query()

##-- List of sites sampled that year
sites_sampled = sorted(site_characteristics_data.keys())
### same thing as a string w/single quotes separated by commas
sites_sampled_string = "'" + "\',\'".join(sites_sampled) + "'" 


#---------------------------------------------------------------------------- 
#---------- DATA QUERIES and GROUPING --------------------------------------   
#----------------------------------------------------------------------------

#----- Get specified sites and year from the Sites database table
#----------------------------------------------------------------------------

#-------------- Construct Query: List of Sites and Year ----------------------
#@profileit(3)
def site_stats_query():
    # First part of query -- is the site in the list of sites sampled, 
    # query will look something like this: site_code in ('site1','site2','site5')
    site_stats_qry = "%s in (%s)" % (utils.siteCol, sites_sampled_string)
    # Combine that with a limit on the date to get only data from the specific year
    # For example:  date_samp_start >= #01-01-2007# and date_samp_start <= #12-31-2007#
    site_stats_qry = "%s and %s >= #01-01-%i# and %s <= #12-31-%i#" % (site_stats_qry, utils.samplestartdateCol, survey_year, utils.samplestartdateCol, survey_year)
    return spatial.TableQuery(gp,sitestats_tbl,site_stats_qry)
    
site_stats = site_stats_query()

#------ Query the Sites Database Table for site id, Zm area, Zm variance with siteid as key
flds_stats = (utils.siteCol,utils.est_basalcovCol,utils.estvar_basalcovCol)
site_stats_data = site_stats.field_results(flds_stats, utils.siteCol)

#----- List of all sites in the Sites DB table meeting the criteria
sites_in_stats_tbl = sorted(site_stats_data.keys())

#---Check for missing sites in the Sites DB table
missing_sites = set(sites_sampled).difference(sites_in_stats_tbl)
if missing_sites:
    err_text = "The sites database table, %s, is missing site(s)\n" % sitestats_tbl
    err_text += ",".join(missing_sites)
    err_text += "\nfor the year, %s" % survey_year
    e.call(err_text)


#--- Determine Analysis Stratum & Extrapolation Type (using geo and sampling strata lookup)
site_extrap = {}
for (siteid,data) in site_characteristics_data.items():
    site_extrap[siteid] = svmp.sw_Stratum4AreaCalcs[tuple(data)]
#--- Create a dictionary of extrapolation types that groups sites
extrap_site = invert_dict(site_extrap)

# Group the site data into lists according to analysis stratum and extrapolation type
core_dat = group_data_by_extrap(extrap_site,svmp.core_extrap,site_stats_data)
pfl_dat = group_data_by_extrap(extrap_site,svmp.pfl_extrap,site_stats_data)
fl_dat = group_data_by_extrap(extrap_site,svmp.fl_extrap,site_stats_data)
fr_dat = group_data_by_extrap(extrap_site,svmp.fr_extrap,site_stats_data)
frw_dat = group_data_by_extrap(extrap_site,svmp.frw_extrap,site_stats_data)

# Get the sample area (from flats shapefile) for each rotational flats site sampled 
fl_sites = extrap_site[svmp.fl_extrap]
# same thing as a string w/single quotes separated by commas
fl_sites_string = "'" + "\',\'".join(fl_sites) + "'" 
# query will look something like this: NAME in ('site1','site2','site5')
fl_sites_qry = "%s in (%s)" % (utils.sitePtIDCol, fl_sites_string)

flats_sampled = spatial.FeatureQuery(gp,flats_fc,fl_sites_qry)

# Dictionary of rotational flats sites with their sample area from flats.shp
flats_a2j = flats_sampled.field_results([flats_sampled.shape_field],utils.sitePtIDCol)
#print flats_a2j
# Append the sample area to the rest of the site data (rotational flats only)
for site in fl_dat:
    a2j = flats_a2j[site[0]][0]
    site.append(a2j)


#---------------------------------------------------------------------------- 
#---------- AREA ESTIMATE CALCULATIONS --------------------------------------   
#----------------------------------------------------------------------------

unit_convert = "sf2m"

print "*** Soundwide Area Estimates for: %s ***" % survey_year

#-- Core Stratum
#@profileit(5)
def core_sample_calc():
    coreStratum = svmp.BaseStratum(svmp.core_extrap[0],svmp.core_extrap[1])
    coreSamp = svmp.SampleStats(core_dat,coreStratum,unit_convert)
    print "******  Core *********"
    print "Count of sites sampled (ni): %i" % coreSamp.ni
    print "Area: %r" % coreSamp.zm_area
    print "Variance: %r" % coreSamp.zm_area_var
    print "s.e.: %r" % coreSamp.se
    print "cv: %r" % coreSamp.cv
    return coreSamp

# -- Persistent Flats Stratum
#@profileit(5)
def persistant_flats_sample_calc():
    pflStratum = svmp.BaseStratum(svmp.pfl_extrap[0],svmp.pfl_extrap[1])
    pflSamp = svmp.SampleStats(pfl_dat,pflStratum,unit_convert)
    print "****** Persistent Flats *********"
    print "Count of sites sampled (ni): %i" % pflSamp.ni
    print "Area: %r" % pflSamp.zm_area
    print "Variance: %r" % pflSamp.zm_area_var
    print "s.e.: %r" % pflSamp.se
    print "cv: %r" % pflSamp.cv
    return pflSamp

# -- Rotational Flats Stratum
#@profileit(15)
def rotational_flats_sample_calc():
    flStratum = svmp.FlatsStratum(svmp.fl_extrap[0],svmp.fl_extrap[1],gp,flats_fc,unit_convert)
    flSamp = svmp.SampleStats(fl_dat,flStratum,unit_convert)
    print "****** Rotational Flats*********"
    print "Count of sites sampled (ni): %i" % flSamp.ni
    print "Ni: %i" % flStratum.Ni
    print "A2: %r" % flStratum.A2
    print "Aij: %r" % flSamp.Aij
    print "R: %r" % flSamp.R
    print "Area: %r" % flSamp.zm_area
    print "Variance: %r" % flSamp.zm_area_var
    print "s.e.: %r" % flSamp.se
    print "cv: %r" % flSamp.cv
    return flSamp


# -- Fringe Stratum
#@profileit(10)
def fringe_sample_calc():
    frStratum = svmp.FringeStratum(svmp.fr_extrap[0],svmp.fr_extrap[1],gp,fringe_fc,unit_convert)
    frSamp = svmp.SampleStats(fr_dat,frStratum,unit_convert)
    print "******  Fringe *********"
    print "Count of sites sampled (ni): %i" % frSamp.ni
    print "Ni: %i" % frStratum.Ni
    print "LT: %r" % frStratum.LT
    print "LN: %r" % frStratum.LN
    print "Area: %r" % frSamp.zm_area
    print "Variance: %r" % frSamp.zm_area_var
    print "s.e.: %r" % frSamp.se
    print "cv: %r" % frSamp.cv
    return frSamp

# -- Wide Fringe Stratum    
#@profileit(10)
def wide_fringe_sample_calc():
    frwStratum = svmp.FringeStratum(svmp.frw_extrap[0],svmp.frw_extrap[1],gp,fringe_fc,unit_convert)
    frwSamp = svmp.SampleStats(frw_dat,frwStratum,unit_convert)
    print "****** Wide Fringe *********"
    print "Count of sites sampled (ni): %i" % frwSamp.ni
    print "Ni: %i" % frwStratum.Ni
    print "LT: %r" % frwStratum.LT
    print "LN: %r" % frwStratum.LN
    print "Area: %r" % frwSamp.zm_area
    print "Variance: %r" % frwSamp.zm_area_var
    print "s.e.: %r" % frwSamp.se
    print "cv: %r" % frwSamp.cv
    return frwSamp

# Do the calculations for all strata
coreSamp = core_sample_calc()
pflSamp = persistant_flats_sample_calc()
flSamp = rotational_flats_sample_calc()
frSamp = fringe_sample_calc()
frwSamp = wide_fringe_sample_calc()

# Open the file for output
outFile = open(outfilename_stratum,'w')
# Column names
colnames_text = ",".join(utils.swAreaStratumCols)
outFile.write(colnames_text + "\n")

# Build up the output data string
#coresamp_string = "%s" % survey_year
#coresamp_string = coresamp_string + ",%s" % coreSamp.stratum.analysis
#coresamp_string = coresamp_string + ",%s" % coreSamp.stratum.extrapolation
#coresamp_string = coresamp_string + ",%s" % sample_group
#coresamp_string = coresamp_string + ",%r" % coreSamp.zm_area
#coresamp_string = coresamp_string + ",%r" % coreSamp.zm_area_var
#coresamp_string = coresamp_string + ",%r" % coreSamp.se
#coresamp_string = coresamp_string + ",%r" % coreSamp.cv
#coresamp_string = coresamp_string + ",%r" % coreSamp.ni
#coresamp_string = coresamp_string + ",%r" % None  # Ni
#coresamp_string = coresamp_string + ",%r" % None # A2
#coresamp_string = coresamp_string + ",%r" % None # Aij
#coresamp_string = coresamp_string + ",%r" % None # R
#coresamp_string = coresamp_string + ",%r" % None # LT
#coresamp_string = coresamp_string + ",%r" % None # LN


# Creates the comma-delimited output string 
#  using formatting based on object type 
def output_string(v1,*vals):
    out_string = "%s" % v1
    for v in vals:
        if type(v) == str:
            out_string = out_string + ",%s" % v
        elif type(v) == int:
            out_string = out_string + ",%i" % v
        else:
            out_string = out_string + ",%r" % v
    out_string = out_string + "\n"
    return out_string

#print output_string(survey_year,coreSamp.stratum.analysis,coreSamp.stratum.extrapolation,sample_group,
                    #coreSamp.zm_area,coreSamp.zm_area_var,coreSamp.se,coreSamp.cv,coreSamp.ni,
                    #"","","","","","")

coreString = output_string(survey_year,coreSamp.stratum.analysis,coreSamp.stratum.extrapolation,sample_group,
                    coreSamp.zm_area,coreSamp.zm_area_var,coreSamp.se,coreSamp.cv,coreSamp.ni,
                    "","","","","","")
pflString = output_string(survey_year,pflSamp.stratum.analysis,pflSamp.stratum.extrapolation,sample_group,
                    pflSamp.zm_area,pflSamp.zm_area_var,pflSamp.se,pflSamp.cv,pflSamp.ni,
                    "","","","","","")
flString = output_string(survey_year,flSamp.stratum.analysis,flSamp.stratum.extrapolation,sample_group,
                    flSamp.zm_area,flSamp.zm_area_var,flSamp.se,flSamp.cv,flSamp.ni,
                    flSamp.stratum.Ni,flSamp.stratum.A2,flSamp.Aij,flSamp.R,"","")
frString = output_string(survey_year,frSamp.stratum.analysis,frSamp.stratum.extrapolation,sample_group,
                    frSamp.zm_area,frSamp.zm_area_var,frSamp.se,frSamp.cv,frSamp.ni,
                    frSamp.stratum.Ni,"","","",frSamp.stratum.LT,frSamp.stratum.LN)
frwString = output_string(survey_year,frwSamp.stratum.analysis,frwSamp.stratum.extrapolation,sample_group,
                    frwSamp.zm_area,frwSamp.zm_area_var,frwSamp.se,frwSamp.cv,frwSamp.ni,
                    frwSamp.stratum.Ni,"","","",frwSamp.stratum.LT,frwSamp.stratum.LN)


#coresamp_string = "%s,%s,%s,%s,%r" % (survey_year,coreSamp.stratum.analysis,coreSamp.stratum.extrapolation,sample_group,coreSamp.zm_area)
outFile.write(coreString)
outFile.write(pflString)
outFile.write(flString)
outFile.write(frString)
outFile.write(frwString)

outFile.close()         


# -- Soundwide (All Strata) Calculations
#@profileit(10)
def annual_sample_calc():
    #print coreSamp.zm_area
    annual = svmp.AnnualEstimate((coreSamp,pflSamp,flSamp,frSamp,frwSamp))
    print "****** Annual Estimate *********"
    print "Area: %r" % annual.zm_area
    print "Variance: %r" % annual.zm_area_var
    print "s.e.: %r" % annual.se
    print "cv: %r" % annual.cv
    return annual

annualCalc = annual_sample_calc()

# Open the file for output
outFile = open(outfilename_all,'w')
# Column names
colnames_text = ",".join(utils.swAreaAllCols)
outFile.write(colnames_text + "\n")

annualString = output_string(survey_year,sample_group,
                    annualCalc.zm_area,annualCalc.zm_area_var,annualCalc.se,annualCalc.cv)
outFile.write(annualString)
outFile.close()         


