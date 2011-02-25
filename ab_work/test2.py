import sys
import os
import arcgisscripting
import svmpUtils

svmp_all_sites_file = "svmp_all_sites.shp"
flats_file = "flats.shp"
fringe_file = "fringe.shp"
stats_gdb = "svmp_sitesdb_lf.mdb"
sites_table = "2008sites"

gp = arcgisscripting.create()

# Get the list of sites and their strata for soundwide sampling sites in specified year
def get_sitestrata(gp,year):
    swfield = "Y%s" % year  # field indicating soundwide sites for specified year
    print swfield 
    # Query should look like this for 2008:    "Y2008" = 1
    query = "\"%s\" = 1" % swfield
    print query
    print svmp_all_sites_file
    
    site_stratum = {}
    
    sites = gp.SearchCursor(svmp_all_sites_file,query)
    site = sites.Next()
    while site:
        siteid = site.getValue("NAME")
        stratum_geo = site.getValue("strata_geo")
        stratum_samp = site.getValue("stratum")
        
        site_stratum[siteid] = (stratum_geo,stratum_samp)
        site = sites.Next()
        
    print site_stratum
    return site_stratum
        
    del sites


# Getting the Area sampled by siteid from flats.shp
def get_area_constants(gp,query):
    flat_areasamp = {}    
    flats = gp.SearchCursor(flats_file,query)
    flat = flats.Next()
    while flat:
        siteid = flat.getValue("NAME")
        area = flat.shape.Area
        print siteid, area
        flat = flats.Next()
        flat_areasamp[siteid] = area
    
    print flat_areasamp 
    return flat_areasamp   
        
    del flats

# Get the Length of the fringe strata
def get_fringe_length(gp,query):
    fringe_length = []
    fringes = gp.SearchCursor(fringe_file,query)
    fringe = fringes.Next()
    while fringe:
        length = fringe.shape.Length
        fringe_length.append(length)
        fringe = fringes.Next()        
    LT = sum(fringe_length)
    return LT   

def get_fringe_count(gp,query):
    count = 0
    fringes = gp.SearchCursor(fringe_file,query)
    fringe = fringes.Next()
    while fringe:
        count += 1
        fringe = fringes.Next()
    Ni = count
    return count


def invert_dict(dict):
    inverse = {}
    for (key, value) in dict.items():
        if value not in inverse:
            inverse[value] = []
        inverse[value].append(key)
    print inverse
    return inverse

##### TESTS 

# geo and sampling strata by site from svmp_all_sites.shp
sw_sitestrata = get_sitestrata(gp,2008)

# Invert this so, strata combos are the keys
sw_stratasite = invert_dict(sw_sitestrata)
print sw_stratasite

# List of rotational flats sites
flr = sw_stratasite.get(('fl','rotational')) # rotational flats sites
print "Rotational flats sites: %s" % flr

# List of core sites and persistent flats
core = sw_stratasite.get(('fl','core'))
print "Core sites, flats only:  %s" % core
core.extend(sw_stratasite.get(('fr','core')))
core.extend(sw_stratasite.get(('frw','core')))
print "Core sites, all: %s" % core

flp = sw_stratasite.get(('fl','persistent'))
print "Persistent Flats sites: %s" % flp
#sites = "\',\'".join(sitelist)
#rfl_query = '"NAME" <> \'\' and "NAME" in (\'%s\')' % sites
core_flp = core + flp
print core_flp


# Area sampled for Rotational Flats sites from flats.shp   
query_flr_year = '"NAME" in (\'%s\')' % "\',\'".join(flr)
print query_flr_year
flr_areasamp = get_area_constants(gp,query_flr_year)
sum_flr_areasamp = sum(flr_areasamp.values()) * svmpUtils.sf2_m2
# sum this
print "Sum of Rotational Flats Area sampled in feet: %s " % sum(flr_areasamp.values())
print "Sum of Rotational Flats Area sampled in meters: %s " % sum_flr_areasamp
# These values match my version of the flats.shp shapefile

#Area sampled for all Rotational Flats stratum from flats.shp
query_flr_all = '"NAME" <> \'\' and "NAME" not in (\'%s\')' % "\',\'".join(core_flp)
print query_flr_all
flr_all_areasamp = get_area_constants(gp,query_flr_all)
sum_flr_all_areasamp = sum(flr_all_areasamp.values()) * svmpUtils.sf2_m2
print "Sum of all Flats Area in feet: %s" % sum(flr_all_areasamp.values())
print "Sum of all Flats Area in meters: %s" % sum_flr_all_areasamp
print "Number of Flats: %s" % len(flr_all_areasamp)


# Get fringe constants
query_fr_worphans = '"2002TYPE" in (\'fr\',\'fr-orphan<984m\') and "region" <> \'sps\''
LT = get_fringe_length(gp,query_fr_worphans)
print "Length of Fringe Stratum in feet: %s" % LT
LT = LT * svmpUtils.sf_m
print "Length of Fringe Stratum in meters: %s" % LT   #This matches the spreadsheet

query_fr = '"2002TYPE" = \'fr\' and "region" <> \'sps\''
Ni = get_fringe_count(gp,query_fr)
print "Count of Sites in Fringe Stratum: %s" % Ni

# Get wide fringe constants
query_fr_worphans = '"2002TYPE" in (\'frw\',\'frw-orphan<984m\') and "region" <> \'sps\''
LT = get_fringe_length(gp,query_fr_worphans)
print "Length of Wide Fringe Stratum in feet: %s" % LT
LT = LT * svmpUtils.sf_m
print "Length of Fringe Stratum in meters: %s" % LT   #This matches the spreadsheet

query_fr = '"2002TYPE" = \'frw\' and "region" <> \'sps\''
Ni = get_fringe_count(gp,query_fr)
print "Count of Sites in Wide Fringe Stratum: %s" % Ni


del gp
    