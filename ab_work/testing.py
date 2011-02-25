# Testing

from svmp import *
import arcgisscripting


def print_attributes(obj):
    for attr in obj.__dict__:
        print attr, getattr(obj, attr)
        
        
def get_sample_data():
    # Create the geoprocessing object
    gp = arcgisscripting.create()
    
# Some example input data of different types
site1 = ["core001",318285957.367152,7.81016158406864E+14] #,"fl","core"]
site2 = ["core002",244910.733927743,364666178.032925] #,"fl","core"]
site3 = ["core003",7126133.7007788,2.64488183159664E+13] #,"fl","core"]
site4 = ["cps2201",906375.318171838,3594387094.67983] #,"fr","rotational"]
site5 = ["cps1967",258515.760930095,334486047.667048] #,"fr","rotational"]
site6 = ["flats42",9491512.37142539,5.30966202206345E+11] #,"fl","rotational"]
site7 = ["flats64",167334.660020894,459109598.450522] #,"fl","rotational"]
site8 = ["flats11",130438027.719328,3.54087547267647E+13] #,"fl","persistent"]
site9 = ["flats12",75198690.7352857,3.04909182172066E+13] #,"fl","persistent"]

site6_aj = ["flats42",41409292.175]
site7_aj = ["flats64",1909264.598]

rfl_samparea = [site6_aj,site7_aj]

# Test core stratum calcs
coreStratum = BaseStratum("fr","core","core","none")
coreSamp = Sample([site1,site2,site3],coreStratum)
print "****** stats for Core*********"
print "Area: %f" % coreSamp.zm_area
print "Variance: %f" % coreSamp.zm_area_var
print "s.e.: %f" % coreSamp.se
print "cv: %f" % coreSamp.cv
#print_attributes(coreSamp)

# Test Flats stratum calcs
print "****** stats for Flats*********"
flsiteslist = [site6,site7]
flStratum = FlatsStratum("fl","rotational","flats","area")
flSamp = Sample(flsiteslist,flStratum)
print "Area: %f" % flSamp.zm_area
print "Variance: %f" % flSamp.zm_area_var
print "s.e.: %f" % flSamp.se
print "cv: %f" % flSamp.cv

print "****** stats for Fringe *********"
frsiteslist = [site4,site5]
frStratum = FringeStratum("fr","rotational","fringe","linear")
frSamp = Sample(frsiteslist, frStratum)
print "Area: %f" % frSamp.zm_area
print "Variance: %f" % frSamp.zm_area_var
print "s.e.: %f" % frSamp.se
print "cv: %f" % frSamp.cv

#print coreSamp

estimate2007 = AnnualEstimate((coreSamp,flSamp,frSamp))
print "****** stats for Soundwide Calcs *********"
print "Area: %f" % estimate2007.zm_area
print "Variance: %f" % estimate2007.zm_area_var
print "s.e.: %f" % estimate2007.se
print "cv: %f" % estimate2007.cv

print estimate2007.zm_areas
print estimate2007.zm_vars

print estimate2007
print_attributes(estimate2007)


#frsiteslist = [site4,site5]
#print frsiteslist


#frSamp = Sample(frsiteslist)
##frSamp.importSites(frsiteslist)
#print "Fringe Sample" 
#print frSamp

#print_attributes(frSamp)
#print frSamp.sites[1]
#print frSamp.sites[1].siteid
#print len(frSamp.sites)
#print frSamp.ni
#print frSamp.countSites()
#print frSamp.ni

#print_attributes(frSamp)

#print frSamp.__dict__
#print frSamp.sites[0].__dict__
#frStrat = FringeStratum("fr","rotational","fringe","linear")
#print frStrat.__dict__
#print frStrat.Ni
#print frStrat

#frSamp.set_stratum(frStrat)
#print frSamp.extrapolation


#print "Fringe ZM area %s" % frSamp.zm_total_area
#print frSamp.stratum.Ni
#print "Fringe ZM Variance %s" % frSamp.calcZmAreaVar()

#flsiteslist = [site6,site7]
#flSample = Sample(flsiteslist)
#flStrat = FlatsStratum("fl","rotational","flats","area")
#flSample.set_stratum(flStrat)

#print "Flats Zm Area %s" % flSample.zm_total_area
#print frSamp.stratum.Ni
#print flSample.calcCV()
#print flSample.stratum.Ni
#print flSample.stratum.A2
#print flSample.stratum.Aij
#print flSample.calcSE()
#print flSample.calcZmAreaVar()

#print flSample.siteids
#print flSample.zmareas
#print flSample.zmvars

#print getattr(flSample,"ZmArea")


### Make individual site objects
##mySite1 = Site((site1[0],site1[1],site1[2],site1[3],site1[4]))
##mySite2 = Site((site2[0],site2[1],site2[2],site2[3],site2[4]))
##mySite3 = Site((site3[0],site3[1],site3[2],site3[3],site3[4]))
##mySite4 = Site((site4[0],site4[1],site4[2],site4[3],site4[4]))
##mySite5 = Site((site5[0],site5[1],site5[2],site5[3],site5[4]))
##mySite6 = Site((site6[0],site6[1],site6[2],site6[3],site6[4]))
##mySite7 = Site((site7[0],site7[1],site7[2],site7[3],site7[4]))
##mySite8 = Site((site8[0],site8[1],site8[2],site8[3],site8[4]))
##mySite9 = Site((site9[0],site9[1],site9[2],site9[3],site9[4]))

### print mySite

##coreSamp = Sample()
##coreSamp.addSite(mySite1)
##coreSamp.addSite(mySite2)
##coreSamp.addSite(mySite3)



