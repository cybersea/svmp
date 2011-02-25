# test_mc.py
# Testing monte carlo 

import svmp_93 as svmp
import arcgisscripting
import copy
import random
import time

gp = arcgisscripting.create(9.3)

## Input
dbPath = "c:/projects/dnr_svmp/output/eelgrass_monitoring/"
blPath = "c:/projects/dnr_svmp/output/eelgrass_monitoring/base_layers/"
outPath = "c:/projects/dnr_svmp/output/eelgrass_monitoring/ab_out/"
siteTable = dbPath  + "svmp_sitesdb_2009_12_21.mdb/all_years_sites"  #"svmp_sitesdb_lf.mdb/2007sites"
allsitesFC = blPath + "svmp_all_sites_041309_samptype.shp"
flatsFC = blPath + "flats.shp"
fringeFC = blPath + "fringe.shp"
surveyYear = 2007
sample_group = "soundwide"   # placeholder -- may be implemented as a parameter later (for soundwide, focus and other sites)
unit_convert = "sf2m"   # unit conversion flag

outFilenameSiteMC = "c:/projects/dnr_svmp/ab_work/test_mc_sites.txt"  # all site data
outFilenameRC = "c:/projects/dnr_svmp/ab_work/test_rc.txt" # relative change values for each iteration

def bootstrap(data):
    new_data = copy.deepcopy(data)
    # Randomly select members from a sample (with replacement)
    #bootstrap_data = [random.choice(new_data) for i in range(len(data))]  # sites duplicated - need a copy
    bootstrap_data = []
    for i in xrange(len(data)):
        mychoice = random.choice(new_data)
        try:
            # If site already exists in bootstrap, make a copy to add
            bootstrap_data.index(mychoice)
            bootstrap_data.append(mychoice[:])
        except:
            # If site doesn't already exist in bootstrap, just add it
            bootstrap_data.append(mychoice)
            
        
    #print data
    #print bootstrap_data
    return bootstrap_data

def match_sites(data1,data2):
    # Find the data from year 2 that match the new, bootstrapped year 1 data
    data2_match = []
    for site in data1:
        site_id = site[0]
        for site in data2:
            try:
                site.index(site_id)
                data2_match.append(site)
                break
            except:
                continue
    return data2_match


def measurement_error(data):
    # Simulate measurement error in the Zm Area estimate
    # using the variance and a random number
    newdata = copy.deepcopy(data)
    print "before measurement error:"
    print data
    print newdata
    for site in newdata:
        zmArea = site[1]
        zmAreaVar = site[2]
        randNum = random.normalvariate(0,1)
        print "------------------------------"
        print "Site %s" % site[0]
        print "Random Number %r" % randNum
        print "Z marina original area %r:" % zmArea
        print "Z marina variance %r" % zmAreaVar
        print "Z marina standard error %r" % (zmAreaVar ** 0.5)
        print "Error to add to Zm area %r" % ((zmAreaVar ** 0.5) * randNum)
        sim_zmArea = zmArea + ((zmAreaVar ** 0.5) * randNum)
        site[1] = sim_zmArea
    print "after measurement error"
    print data
    print newdata
    return newdata


# Test measurement error for a single site

def measure_error_test():
    mysite = svmp.Site(1,200,0.3)
    print mysite

    newsite = mysite.simulate()
    # creates a new site object with simulated data
    print mysite
    print newsite

#measure_error_test()

# SAMPLE DATA
# 2007 all data
frw_sitedata = [[u'nps1387', 454278.19657953392, 565317573.18556392], [u'nps1433', 340583.19406011031, 237968078.2567277], [u'nps1320', 1296743.5015554917, 6190220703.6047506], [u'nps1328', 67824.704233520024, 1320615379.8151431], [u'hdc2383', 367260.47592005413, 5788626438.1929483], [u'hdc2284', 488538.60463107051, 2944841450.5675225], [u'swh0955', 830636.94363810716, 706437579.36770582], [u'sjs2775', 536635.86658442533, 1209353099.8771534], [u'hdc2283', 864521.65260779834, 19692087276.48975], [u'cps169', 1006018.5328661726, 8889942318.4616241], [u'sjs2742', 0.0, 0.0], [u'swh0881', 0.0, 0.0], [u'swh0869', 6528.3419565173335, 14765082.756849209],[u'cps1160', 252868.13608286722, 884819397.36503839], [u'swh0918', 1472638.480749303, 6217391680.3640585]]
# 2007 match data
frw_y1matchdata = [[u'nps1387', 454278.19657953392, 565317573.18556392], [u'sjs2742', 0.0, 0.0], [u'nps1433', 340583.19406011031, 237968078.2567277], [u'nps1328', 67824.704233520024, 1320615379.8151431], [u'hdc2283', 864521.65260779834, 19692087276.48975], [u'hdc2284', 488538.60463107051, 2944841450.5675225], [u'swh0881', 0.0, 0.0], [u'swh0869', 6528.3419565173335, 14765082.756849209], [u'hdc2383', 367260.47592005413, 5788626438.1929483], [u'cps1160', 252868.13608286722, 884819397.36503839], [u'swh0955', 830636.94363810716, 706437579.36770582], [u'swh0918', 1472638.4807493303, 6217391680.3640585]]
# 2008 match data
frw_y2matchdata = [[u'nps1387', 391810.93579751794, 1711787273.5598774], [u'sjs2742', 0.0, 0.0], [u'nps1433', 310158.22380991612, 595748883.00832057], [u'nps1328', 267365.24879528332, 3988164714.8396354], [u'hdc2283', 924844.61956966901, 13203803928.720116], [u'hdc2284', 1030121.7722244665, 8875346586.0276794], [u'swh0881', 0.0, 0.0], [u'swh0869', 8166.2397642551814, 6070942.5022775074], [u'hdc2383', 461831.29724269669, 7079312762.6476727], [u'cps1160', 214160.87377709564, 929840467.35095119], [u'swh0955', 885493.30819616525, 2193937155.4220476], [u'swh0918', 1599381.5539709965, 9880620715.7350445]]


frwStratum = svmp.FringeStratum(svmp.fr_extrap[0],svmp.fr_extrap[1],gp,fringeFC,unit_convert)
mysample = svmp.Sample(frw_sitedata,frwStratum,unit_convert)


def bootstrap_test1():
    for site in mysample.sites:
        newsite = site.simulate()
        print site
        print newsite

    #print mysample
    print mysample
    print mysample.ni
    mysample.bootstrap()
    print mysample
    print mysample.ni

#bootstrap_test1()

frw1 = svmp.Sample(frw_y1matchdata,frwStratum,unit_convert)
frw2 = svmp.Sample(frw_y2matchdata,frwStratum,unit_convert)

# Get the bootstrapped sample from the first year of matching data
def bootstrap_test2():
    print frw1
    print frw1.ni
    print frw1.site_ids
    frw1bs = copy.copy(frw1)
    
    # make a copy of the object for bootstrapping
    print frw1bs.bootstrap()
    print frw1bs.ni
    print frw1bs.site_ids
    print frw1.site_ids
    # Then, find matching sites (to bootstrap) from Year 2
    

def bootstrap_test3():
    # bootstrap the source data, rather than the sample object
    print frw_y1matchdata
    print len(frw_y1matchdata)
    bsy1m = bootstrap(frw_y1matchdata)
    print bsy1m
    print len(bsy1m)
    # Then get the matching data from Y2 data
    bsy2m = []
    for site in bsy1m:
        site_id = site[0]
        print site_id
        for site in frw_y2matchdata:
            try:
                site.index(site_id)
                print site
                bsy2m.append(site)
                break
            except:
                continue
    print bsy2m
    
    # Bootstrap of full year 1 data
    bsy1all = bootstrap(frw_sitedata)
    print frw_sitedata
    print bsy1all
    
    return bsy1all,bsy1m,bsy2m


def measure_error_test1():
    y1allmese = measurement_error(bsy1all)
    print y1allmese

  
#(bs1,bs1m,bs2m) = bootstrap_test3()

# Original data
print "Source Data"
print frw_sitedata
#for site in frw_sitedata:
    #print "%s,%r,%r" % (site[0],site[1],site[2])
print frw_y1matchdata
#for site in frw_y1matchdata:
    #print "%s,%r,%r" % (site[0],site[1],site[2])
print frw_y2matchdata
#for site in frw_y2matchdata:
    #print "%s,%r,%r" % (site[0],site[1],site[2])

yr1Samp  = svmp.SampleStats(frw_sitedata,frwStratum,unit_convert)
yr1mSamp = svmp.SampleStats(frw_y1matchdata,frwStratum,unit_convert)
yr2mSamp = svmp.SampleStats(frw_y2matchdata,frwStratum,unit_convert)
frwChange = svmp.ChangeStats(yr1mSamp,yr2mSamp,yr1Samp)

print "Original Proportion Change: %r" % frwChange.change_prop

## Bootstrap -- select a random set of sites
#bs1 = bootstrap(frw_sitedata)
#bs1m = bootstrap(frw_y1matchdata)
#bs2m = match_sites(bs1m,frw_y2matchdata)
##print bs1
##print bs1m
##print bs2m

## Measurement error -- 
## -- simulate a Zm Area using variance and a random number
#me1 = measurement_error(bs1)
#me1m = measurement_error(bs1m)
#me2m = measurement_error(bs2m)

##print me1
##print me1m
##print me2m

## Then, get new area estimates
#yr1Samp  = svmp.SampleStats(me1,frwStratum,unit_convert)
#yr1mSamp = svmp.SampleStats(me1m,frwStratum,unit_convert)
#yr2mSamp = svmp.SampleStats(me2m,frwStratum,unit_convert)

#frwChange = svmp.ChangeStats(yr1mSamp,yr2mSamp,yr1Samp)

#print frwChange.change_prop

def conf95(rel_changes):
    # Takes a list of relative change values
    # and finds the mean and the 95% confidence interval
    mean_rc = sum(rel_changes) / len(rel_changes)
    sort_rcs = sorted(rel_changes[:])
    print rel_changes
    print sort_rcs
    #conf_intervals = [abs(mean_rc - v) for v in sort_rcs]
    conf_intervals = [abs(mean_rc - rc) for rc in rel_changes]
    print conf_intervals
    cis_sorted = sorted(conf_intervals)
    print cis_sorted
    

outFileSiteMC = open(outFilenameSiteMC,'w')
outFileRC = open(outFilenameRC,'w')

rel_changes = []
# ----- Do 20000 iterations -----
def all_steps():
    print time.asctime()
    iterations = 20
    sum_rc = 0
    for i in range(iterations):
        bs1 = bootstrap(frw_sitedata)
        bs1m = bootstrap(frw_y1matchdata)
        bs2m = match_sites(bs1m,frw_y2matchdata)
        me1 = measurement_error(bs1)
        #print me1
        me1m = measurement_error(bs1m)
        #print me1m
        me2m = measurement_error(bs2m)
        #print me2m
        yr1Samp  = svmp.SampleStats(me1,frwStratum,unit_convert)
        yr1mSamp = svmp.SampleStats(me1m,frwStratum,unit_convert)
        yr2mSamp = svmp.SampleStats(me2m,frwStratum,unit_convert)  
        frwChange = svmp.ChangeStats(yr1mSamp,yr2mSamp,yr1Samp)
        rc = frwChange.change_prop
        print "Relative Change %r" % rc
        rcString = "%i,%r\n" % (i+1,rc)
        rel_changes.append(rc)
        #sum_rc = sum_rc + rc
        outFileRC.write(rcString)
        
    mean_rc = sum(rel_changes)/ iterations
    print "Mean Relative Change %r" % mean_rc
    print time.asctime()
    conf95(rel_changes)
    
    



mybs = bootstrap(frw_sitedata)
print mybs

for i1,site1 in enumerate(mybs):
    for i2,site2 in enumerate(mybs):
        if site1 is site2:
            print i1,site1,i2,site2
            

all_steps()

outFileSiteMC.close()
outFileRC.close()
    