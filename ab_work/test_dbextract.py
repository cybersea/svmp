# Database extraction testing

import sys
import os
import arcgisscripting

stats_gdb = "svmp_sitesdb_lf.mdb"
sites_table = "2007sites"
sites_tab_fullpath = "svmp_sitesdb_lf.mdb\\2007sites"
survey_year = 2007
date_field = "[date_samp_start]"
fld_area = "zm_area_ft2"
fld_var = "zm_area_var_ft4"


gp = arcgisscripting.create()


# Query for single year of data
# [date_samp_start] >= #01-01-2007# and [date_samp_start] <= #12-31-2007#

query = "%s >= #01-01-%i# and %s <= #12-31-%i#" % (date_field, survey_year, date_field, survey_year)

print query

sites = gp.SearchCursor(sites_tab_fullpath,query)
print sites
site = sites.Next()
print site
    


del gp