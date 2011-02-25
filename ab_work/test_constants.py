import arcgisscripting
import svmp
import svmp_spatial

# ----------- PARAMETERS ----------------------------------
# Temporary stand-ins for parameters
sitestats_tbl = "svmp_sitesdb_lf.mdb/2007sites"
svmp_all_sites_fc = "svmp_all_sites_041309_samptype.shp"
flats_fc = "flats.shp"
fringe_fc = "fringe.shp"
survey_year = 2007
sample_group = "sw"   # placeholder -- may be implemented as a parameter later (for soundwide, focus and other sites)

unit_convert = "sf2m"

gp = arcgisscripting.create()

flConstants = svmp.FlatsStratumConstants(gp,flats_fc,unit_convert)

print "Ni: %i" % flConstants.Ni
print "A2: %f" % flConstants.A2

frConstants = svmp.FringeStratumConstants("fringe",gp,fringe_fc,unit_convert)

print "Ni: %i" % frConstants.Ni
print "LT: %f" % frConstants.LT