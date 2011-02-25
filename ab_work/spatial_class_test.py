import arcgisscripting
import svmp_spatial


svmp_all_sites_file = "svmp_all_sites.shp"
flats_file = "flats.shp"
fringe_file = "fringe.shp"
stats_gdb = "svmp_sitesdb_lf.mdb"
sites_table = "2008sites"

gp = arcgisscripting.create()


query = "\"NAME\" <> '' and \"NAME\" not in ('core001','core002','core003','core004','core006','core005','flats11','flats12','flats20')"

print query

fl_query = svmp_spatial.FeatureQuery(gp,flats_file,query)

print "Feature Class: %s" % fl_query.fc
print fl_query.geom_type
print "Geometry sum: %f %s" % (fl_query.geometry_sum, fl_query.get_linear_units())
print "Record Count: %i" % fl_query.record_count

flats_results = fl_query.field_results(("NAME","REGION","Shape"))
print flats_results
print len(flats_results)
print fl_query.shape_field

print fl_query.get_field_list()
          
#query = "\"2002TYPE\" in ('fr','fr-orphan<984m') and \"region\" <> 'sps'"
#fr_w_orphan_query = svmp_spatial.FeatureQuery(gp,fringe_file,query)

#print "\n"
#print "Feature Class: %s" % fr_w_orphan_query.fc
#print fr_w_orphan_query.geom_type
#print "Geometry sum: %f %s" % (fr_w_orphan_query.geometry_sum, fr_w_orphan_query.get_linear_units())
#print "Record Count: %i" % fr_w_orphan_query.record_count

del gp