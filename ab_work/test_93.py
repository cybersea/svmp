import arcgisscripting
import svmp_spatial_93 as spatial
import svmpUtils as utils

shp = "svmp_all_sites_041309_samptype.shp"
tbl = "svmp_sitesdb_lf.mdb/2007sites"
flats_fc = "flats.shp"

#---- Create the Geoprocessing Object, v.9.3 ----------------------
gp = arcgisscripting.create(9.3)

#---- Testing Table Query object
# List fields
tq = spatial.TableQuery(gp,shp)
print tq.fields

# Get field Results
test_fields = [utils.siteGeoStratCol,utils.siteSampStratCol]
fr = tq.field_results(test_fields)
print fr

# Record count
print tq.record_count

#---- Testing Feature Query object
fq = spatial.FeatureQuery(gp,flats_fc)
print fq.fields
print fq.geom_type
print fq.shape_field
print fq.get_linear_units()
print fq.geometry_sum

