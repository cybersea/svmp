import arcgisscripting
import svmp 
import svmp_spatial as spatial
import svmpUtils as utils
from svmp_exceptions import SvmpToolsError

# ----------- PARAMETERS ----------------------------------
# Temporary stand-ins for parameters
sitestats_tbl = "svmp_sitesdb_lf.mdb/2007sites"
svmp_all_sites_fc = "svmp_all_sites_041309_samptype.shp"
flats_fc = "flats.shp"
fringe_fc = "fringe.shp"
survey_year = 2007
sample_group = "sw"   # placeholder -- may be implemented as a parameter later (for soundwide, focus and other sites)


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
    # get the list of sites for the specified analysis stratum and extrapolation
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

if sample_group == "sw":
    #-------------- Construct Query: Soundwide sites for the specified year ---
    samp_type_qry = "%s in ('sw','sw_focus','sw_other')" % samp_type_field

# Query the All Sites feature class
site_characteristics =  spatial.TableQuery(gp,svmp_all_sites_fc,samp_type_qry)

#----- Query All Sites Table for geomorph stratum, and sampling stratum with siteid as key
flds_c = [utils.siteGeoStratCol,utils.siteSampStratCol]
site_characteristics_data = site_characteristics.field_results(flds_c,utils.sitePtIDCol)
#print site_characteristics_data

##-- List of sites sampled that year
sites_sampled = sorted(site_characteristics_data.keys())
#print '+'*90
#print sites_sampled
### same thing as a string w/double quotes separated by commas
sites_sampled_string = '"' + "\",\"".join(sites_sampled) + '"' 
#print sites_sampled_string

#---------------------------------------------------------------------------- 
#---------- DATA QUERIES and GROUPING --------------------------------------   
#----------------------------------------------------------------------------

#----- Get specified sites and year from the Sites database table
#----------------------------------------------------------------------------

#-------------- Construct Query: List of Sites and Year ----------------------
# First part of query -- is the site in the list of sites sampled, 
# query will look something like this: site_code in ("site1","site2","site5")
site_stats_qry = "%s in (%s)" % (utils.siteCol, sites_sampled_string)
# Combine that with a limit on the date to get only data from the specific year
# For example:  date_samp_start >= #01-01-2007# and date_sampe_start <= #12-31-2007#
site_stats_qry = "%s and %s >= #01-01-%i# and %s <= #12-31-%i#" % (site_stats_qry, utils.samplestartdateCol, survey_year, utils.samplestartdateCol, survey_year)
site_stats = spatial.TableQuery(gp,sitestats_tbl,site_stats_qry)

#------ Query the Sites Database Table for site id, Zm area, Zm variance with siteid as key
flds_stats = (utils.siteCol,utils.est_basalcovCol,utils.estvar_basalcovCol)
site_stats_data = site_stats.field_results(flds_stats, utils.siteCol)
#print 'site_stats_data-->\n'
#print site_stats_data

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
#print site_extrap
#--- Create a dictionary of extrapolation types that groups sites
extrap_site = invert_dict(site_extrap)
#print extrap_site

core_dat = group_data_by_extrap(extrap_site,svmp.core_extrap,site_stats_data)
pfl_dat = group_data_by_extrap(extrap_site,svmp.pfl_extrap,site_stats_data)
fl_dat = group_data_by_extrap(extrap_site,svmp.fl_extrap,site_stats_data)
fr_dat = group_data_by_extrap(extrap_site,svmp.fr_extrap,site_stats_data)
frw_dat = group_data_by_extrap(extrap_site,svmp.frw_extrap,site_stats_data)

    
#print core_dat
#print pfl_dat
#print fl_dat
#print fr_dat
#print frw_dat

#---------------------------------------------------------------------------- 
#---------- AREA ESTIMATE CALCULATIONS --------------------------------------   
#----------------------------------------------------------------------------

unit_convert = "sf2m"

print "*** Soundwide Area Estimates for: %s ***" % survey_year
#-- Core Stratum
coreStratum = svmp.BaseStratum(svmp.core_extrap[0],svmp.core_extrap[1])
coreSamp = svmp.Sample(core_dat,coreStratum,unit_convert)
print "****** stats for Core *********"
print "Area: %f" % coreSamp.zm_area
print "Variance: %f" % coreSamp.zm_area_var
print "s.e.: %f" % coreSamp.se
print "cv: %f" % coreSamp.cv

# -- Persistent Flats Stratum
pflStratum = svmp.BaseStratum(svmp.pfl_extrap[0],svmp.pfl_extrap[1])
pflSamp = svmp.Sample(pfl_dat,pflStratum,unit_convert)
print "****** stats for Persistent Flats *********"
print "Area: %f" % pflSamp.zm_area
print "Variance: %f" % pflSamp.zm_area_var
print "s.e.: %f" % pflSamp.se
print "cv: %f" % pflSamp.cv

# -- Rotational Flats Stratum
flStratum = svmp.FlatsStratum(svmp.fl_extrap[0],svmp.fl_extrap[1],flats_fc,gp,unit_convert)
flSamp = svmp.Sample(fl_dat,flStratum,unit_convert)
print "****** stats for Flats*********"
print "Ni: %i" % flStratum.Ni
print "A2: %f" % flStratum.A2
print "Area: %f" % flSamp.zm_area
print "Variance: %f" % flSamp.zm_area_var
print "s.e.: %f" % flSamp.se
print "cv: %f" % flSamp.cv

# -- Fringe Stratum
frStratum = svmp.FringeStratum(svmp.fr_extrap[0],svmp.fr_extrap[1],fringe_fc,gp,unit_convert)
frSamp = svmp.Sample(fr_dat,frStratum,unit_convert)
print "****** stats for Fringe *********"
print "Ni: %i" % frStratum.Ni
print "LT: %f" % frStratum.LT
print "Area: %f" % frSamp.zm_area
print "Variance: %f" % frSamp.zm_area_var
print "s.e.: %f" % frSamp.se
print "cv: %f" % frSamp.cv

# -- Wide Fringe Stratum    
frwStratum = svmp.FringeStratum(svmp.frw_extrap[0],svmp.frw_extrap[1],fringe_fc,gp,unit_convert)
#import pdb;pdb.set_trace()
frwSamp = svmp.Sample(frw_dat,frwStratum,unit_convert)
print "****** stats for Wide Fringe *********"
print "Ni: %i" % frwStratum.Ni
print "LT: %f" % frwStratum.LT
print "Area: %f" % frwSamp.zm_area
print "Variance: %f" % frwSamp.zm_area_var
print "s.e.: %f" % frwSamp.se
print "cv: %f" % frwSamp.cv
 
# -- Soundwide (All Strata
annual = svmp.AnnualEstimate((coreSamp,pflSamp,flSamp,frSamp,frwSamp))
print "****** stats for Annual Estimate *********"
print "Area: %f" % annual.zm_area
print "Variance: %f" % annual.zm_area_var
print "s.e.: %f" % annual.se
print "cv: %f" % annual.cv
