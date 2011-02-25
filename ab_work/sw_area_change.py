import sys
import arcgisscripting
import svmp 
import svmp_spatial as spatial
import svmpUtils as utils
from svmp_exceptions import SvmpToolsError
from profiling import profileit

# ----------- PARAMETERS ----------------------------------
# Temporary stand-ins for parameters
sitestats_y1tbl = "svmp_sitesdb_2009_12_21.mdb/2007sites"
sitestats_y2tbl = "svmp_sitesdb_2009_12_21.mdb/2008sites"

svmp_all_sites_fc = "svmp_all_sites_041309_samptype.shp"
year1 = 2007
year2 = 2008
# placeholder -- may be implemented as a parameter later 
#    (for soundwide, focus and other sites)
sample_group = "soundwide" 

flats_fc = "flats.shp"
fringe_fc = "fringe.shp"

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


def query_results(gp,fc,return_fields,query_string,key_field = None):
    """ Generic function for creating ArcGIS query object and returning results """
    query = spatial.TableQuery(gp,fc,query_string)
    results = query.field_results(return_fields,key_field)
    return results

def sites_strata(gp,fc,group,year1,year2=None):
    """ Create dictionary of sites sampled in a single year or 
        matching sites sampled in both years
        from a particular "group" (soundwide being the only implemented option)
    """
    return_fields = [utils.siteGeoStratCol,utils.siteSampStratCol]   # STRATA_GEO, STRATUM
    key_field = utils.sitePtIDCol   # NAME    
    if group == "soundwide":
        #------ Query String: Soundwide sites for the specified years ---
        # -- Should look like this: "Y2008" = 1
        yr1_field = "Y%s" % year1
        query_string = "%s = 1" % (yr1_field)
        if year2 is not None:
            yr2_field = "Y%s" % year2
            query_string += " and %s = 1" % (yr2_field)
            
    results = query_results(gp,fc,return_fields,query_string,key_field)
    return results
    
##--Extract data from sites statistics database using site ID query
def sites_data(gp,sites,year,table):
    ''' Create a dictionary of sites and their associated Zm area and variance '''
    siteid_field = utils.siteCol   # site_code
    date_field = utils.samplestartdateCol
    return_fields = (utils.siteCol,utils.est_basalcovCol,utils.estvar_basalcovCol) 
    #------ Query String: List of sites within the specified year ---
    #  Example:  site_code in ('core001','core002','core005')
    query_string = "%s in (%s)" % (siteid_field, sites)
    # Example: date_samp_start >= #01-01-2007# and date_samp_start <= #12-31-2007#
    query_string += " and %s >= #01-01-%i# and %s <= #12-31-%i#" % (date_field, year, date_field, year)   
    results = query_results(gp,table,return_fields,query_string,siteid_field)
    return results

def missing_site_check(master_list,sites2check,table,year):
    ''' Checks for missing sites based on a master list 
        Generates error text and calls error object if missing
    '''
    missing_sites = set(master_list).difference(sites2check)
    if missing_sites:
        err_text = "The sites database table, %s, is missing site(s)\n" % table
        err_text += ",".join(missing_sites)
        err_text += "\nfor the year, %s" % year
        e.call(err_text)

def strata_lookup(sites_strata,lookup_dict):
    '''Create dictionary of extrapolation type by site id
       using lookup from analysis/geo stratum to 
       determine analysis and extrapolation type
    '''
    site_extrap = {}
    for (siteid,data) in sites_strata.items():
        site_extrap[siteid] = lookup_dict[tuple(data)]
    # invert this dictionary to get sites by extrapolation/analysis stratum
    extrap_site = invert_dict(site_extrap)
    return extrap_site

#---- Create the Geoprocessing Object ----------------------
gp = arcgisscripting.create()

#----- Create the Custom Error Object ----------------------
e = SvmpToolsError(gp)
# Set some basic defaults for error handling
e.debug = True
e.full_tb = True

#-------- unit conversion flag --------------------
unit_convert = "sf2m"

#------------------   DATA QUERIES AND GROUPING --------------------------------
#-------------------------------------------------------------------------------
#----------------- MATCHING SITES sampled in YEARS 1 & 2 -----------------------
#-------------------------------------------------------------------------------
# Get list of sites sampled in both years and their strata
sites_strata_2yr = sites_strata(gp,svmp_all_sites_fc,sample_group,year1,year2)
sites2yr = sorted(sites_strata_2yr.keys())
# For use in query strings
sites2yr_string = "'" + "\',\'".join(sites2yr) + "'" 

# Get data from site stats database table for the matching sites
data_y1m = sites_data(gp,sites2yr_string,year1,sitestats_y1tbl)
data_y2m = sites_data(gp,sites2yr_string,year2,sitestats_y2tbl)

# Check for missing sites in sites stats DB query results
missing_site_check(sites2yr,data_y1m.keys(),sitestats_y1tbl,year1)
missing_site_check(sites2yr,data_y2m.keys(),sitestats_y2tbl,year2)

## Sites grouped by extrapolation type
extrap_sites2yr = strata_lookup(sites_strata_2yr,svmp.sw_Stratum4AreaChgCalcs)

# Group matching site data into lists by analysis/extrapolation type
core_y1m = group_data_by_extrap(extrap_sites2yr,svmp.core_extrap,data_y1m)
fl_y1m = group_data_by_extrap(extrap_sites2yr,svmp.fl_extrap,data_y1m)
fr_y1m = group_data_by_extrap(extrap_sites2yr,svmp.fr_extrap,data_y1m)
frw_y1m = group_data_by_extrap(extrap_sites2yr,svmp.frw_extrap,data_y1m)

core_y2m = group_data_by_extrap(extrap_sites2yr,svmp.core_extrap,data_y2m)
fl_y2m = group_data_by_extrap(extrap_sites2yr,svmp.fl_extrap,data_y2m)
fr_y2m = group_data_by_extrap(extrap_sites2yr,svmp.fr_extrap,data_y2m)
frw_y2m = group_data_by_extrap(extrap_sites2yr,svmp.frw_extrap,data_y2m)

# Get the sample area (from flats shapefile) for rotational flats sites
# and append to rotational flats data
def add_samplearea(flats_data,extrap_sites):
    fl_sites = extrap_sites[svmp.fl_extrap]
    fl_sites_string = "'" + "\',\'".join(fl_sites) + "'" 
    siteid_field = utils.sitePtIDCol   # NAME    
    # query will look something like this: NAME in ('site1','site2','site5')
    query_string = "%s in (%s)" % (siteid_field, fl_sites_string)
    flats_query = spatial.FeatureQuery(gp,flats_fc,query_string)
    # Dictionary of rotational flats sites with their sample area from flats.shp
    flats_a2j = flats_query.field_results([flats_query.shape_field],siteid_field)
    
    # Append the sample area to the rest of the site data (rotational flats only)
    for site in flats_data:
        a2j = flats_a2j[site[0]][0]
        site.append(a2j)
        
    return flats_data

fl_y1m = add_samplearea(fl_y1m,extrap_sites2yr)
fl_y2m = add_samplearea(fl_y2m,extrap_sites2yr)

#--------------------- End MATCHING SITES --------------------------------------
    
#----------------------- ALL SITES sampled in YEAR 1 ---------------------------
# Get list of sites from Year 1 and associated strata
sites_strata_y1 = sites_strata(gp,svmp_all_sites_fc,sample_group,year1)
sites_y1 = sorted(sites_strata_y1.keys())
# For use in query strings
sites_y1_string = "'" + "\',\'".join(sites_y1) + "'" 

# Get data from site stats database table
data_y1 = sites_data(gp,sites_y1_string,year1,sitestats_y1tbl)

# Check for missing sites in sites stats DB query results
missing_site_check(sites_y1,data_y1.keys(),sitestats_y1tbl,year1)

# Sites grouped by extrapolation type
extrap_sites_y1 = strata_lookup(sites_strata_y1,svmp.sw_Stratum4AreaChgCalcs)

# Group site data into lists by analysis/extrapolation type
core_y1 = group_data_by_extrap(extrap_sites_y1,svmp.core_extrap,data_y1)
fl_y1 = group_data_by_extrap(extrap_sites_y1,svmp.fl_extrap,data_y1)
fr_y1 = group_data_by_extrap(extrap_sites_y1,svmp.fr_extrap,data_y1)
frw_y1 = group_data_by_extrap(extrap_sites_y1,svmp.frw_extrap,data_y1)

fl_y1 = add_samplearea(fl_y1,extrap_sites_y1)

#----------------------- End SITES sampled in YEAR 1 ---------------------------

#------------------   End DATA QUERIES AND GROUPING ----------------------------
#-------------------------------------------------------------------------------

#-------------------------------- CALCULATIONS ---------------------------------
#---------------------------------- Strata -------------------------------------
# Performs Sample Calculations for 
# Year 1 matching sites, Year 2 matching sites, and Year 1 all sites
# This is necessary input to Change Analysis Calculations

def core_sample_calc(data):
    coreStratum = svmp.BaseStratum(svmp.core_extrap[0],svmp.core_extrap[1])
    coreSamp = svmp.SampleStats(data,coreStratum,unit_convert)
    return coreSamp
coreSamp_y1m = core_sample_calc(core_y1m)
coreSamp_y2m = core_sample_calc(core_y2m)
coreSamp_y1 = core_sample_calc(core_y1)
coreChange = svmp.ChangeStats(coreSamp_y1m,coreSamp_y2m,coreSamp_y1)

def flats_sample_calc(data):
    flatsStratum = svmp.FlatsStratum(svmp.fl_extrap[0],svmp.fl_extrap[1],gp,flats_fc,unit_convert)
    flatsSamp = svmp.SampleStats(data,flatsStratum,unit_convert)
    return flatsSamp
flSamp_y1m = flats_sample_calc(fl_y1m)
flSamp_y2m = flats_sample_calc(fl_y2m)
flSamp_y1 = flats_sample_calc(fl_y1)
flChange = svmp.ChangeStats(flSamp_y1m,flSamp_y2m,flSamp_y1)

def fringe_sample_calc(data):
    fringeStratum = svmp.FringeStratum(svmp.fr_extrap[0],svmp.fr_extrap[1],gp,fringe_fc,unit_convert)
    fringeSamp = svmp.SampleStats(data,fringeStratum,unit_convert)
    return fringeSamp
frSamp_y1m = fringe_sample_calc(fr_y1m)
frSamp_y2m = fringe_sample_calc(fr_y2m)
frSamp_y1 = fringe_sample_calc(fr_y1)
frChange = svmp.ChangeStats(frSamp_y1m,frSamp_y2m,frSamp_y1)

def wide_fringe_sample_calc(data):
    fringewideStratum = svmp.FringeStratum(svmp.frw_extrap[0],svmp.frw_extrap[1],gp,fringe_fc,unit_convert)
    fringewideSamp = svmp.SampleStats(data,fringewideStratum,unit_convert)
    return fringewideSamp
frwSamp_y1m = wide_fringe_sample_calc(frw_y1m)
frwSamp_y2m = wide_fringe_sample_calc(frw_y2m)
frwSamp_y1 = wide_fringe_sample_calc(frw_y1)
frwChange = svmp.ChangeStats(frwSamp_y1m,frwSamp_y2m,frwSamp_y1)

#--------------------------- Totals ALL STRATA Combined ------------------------
#-------------------------------------------------------------------------------
def annual_sample_calc(samples):
    annual = svmp.AnnualEstimate(samples)
    #print "****** Annual Estimate, Year 1 *********"
    #print "Area: %r" % annual.zm_area
    #print "Variance: %r" % annual.zm_area_var
    #print "s.e.: %r" % annual.se
    #print "cv: %r" % annual.cv
    return annual

# Annual Estimate for Year 1, All strata combined
y1annualCalc = annual_sample_calc((coreSamp_y1,flSamp_y1,frSamp_y1,frwSamp_y1))

zmChangeAll = svmp.ChangeStatsTotal((coreChange,flChange,frChange,frwChange),y1annualCalc)

#------------------------------ End CALCULATIONS -------------------------------
#-------------------------------------------------------------------------------

#-----------------------------------   OUTPUT ----------------------------------
#-------------------------------------------------------------------------------

def output_strata(label,changeObj):
    print "******  %s *********" % label
    print "Year 1 Area: %r" % changeObj.y1.zm_area
    print "Year 1 Variance: %r" % changeObj.y1.zm_area_var
    print "Year 1 Site Count: %i" % changeObj.y1.ni
    print "Matching Site Count: %i" % changeObj.y1m.ni
    print "Slope: %r" % changeObj.m
    print "S.E. of Slope: %r" % changeObj.m_se
    print "Proportion Change: %r" % changeObj.change_prop
    print "Percent Change: %r" % (changeObj.change_prop * 100)
    print "Area Change (m2): %r" % changeObj.area_change
    print "S.E. of Area Change: %r" % changeObj.area_change_se

print "Zostera Marina Soundwide Change Stats for %i to %i" % (year1,year2)
output_strata("Core",coreChange)
output_strata("Flats",flChange)
output_strata("Fringe",frChange)
output_strata("Wide Fringe",frwChange)

def output_sw(label,changeObj):
    print "******  %s *********" % label
    print "Proportion Change: %r" % changeObj.change_prop
    print "Percent Change: %r" % (changeObj.change_prop * 100)
    print "Area Change (m2): %r" % changeObj.area_change
    print "S.E. of Area Change: %r" % changeObj.area_change_se

output_sw("Soundwide",zmChangeAll)

# Used for Debugging
def sites_out(label,changeObj):
    print "%s" % label
    for s1,s2,a1,a2 in zip(changeObj.y1m.site_ids,changeObj.y2m.site_ids,changeObj.y1m.zm_areas,changeObj.y2m.zm_areas):
        print "%s,%s,%r,%r" % (s1,s2,a1,a2)

#sites_out("Core",coreChange)
#sites_out("Flats",flChange)
#sites_out("Fringe",frChange)
#sites_out("Wide Fringe",frwChange)

#--------------------------------- End  OUTPUT ---------------------------------
#-------------------------------------------------------------------------------
