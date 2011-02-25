# test_mc2.py
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

# SAMPLE DATA
# 2007 all data
frw_sitedata = [[u'nps1387', 454278.19657953392, 565317573.18556392], [u'nps1433', 340583.19406011031, 237968078.2567277], [u'nps1320', 1296743.5015554917, 6190220703.6047506], [u'nps1328', 67824.704233520024, 1320615379.8151431], [u'hdc2383', 367260.47592005413, 5788626438.1929483], [u'hdc2284', 488538.60463107051, 2944841450.5675225], [u'swh0955', 830636.94363810716, 706437579.36770582], [u'sjs2775', 536635.86658442533, 1209353099.8771534], [u'hdc2283', 864521.65260779834, 19692087276.48975], [u'cps169', 1006018.5328661726, 8889942318.4616241], [u'sjs2742', 0.0, 0.0], [u'swh0881', 0.0, 0.0], [u'swh0869', 6528.3419565173335, 14765082.756849209],[u'cps1160', 252868.13608286722, 884819397.36503839], [u'swh0918', 1472638.480749303, 6217391680.3640585]]
# 2007 match data
frw_y1matchdata = [[u'nps1387', 454278.19657953392, 565317573.18556392], [u'sjs2742', 0.0, 0.0], [u'nps1433', 340583.19406011031, 237968078.2567277], [u'nps1328', 67824.704233520024, 1320615379.8151431], [u'hdc2283', 864521.65260779834, 19692087276.48975], [u'hdc2284', 488538.60463107051, 2944841450.5675225], [u'swh0881', 0.0, 0.0], [u'swh0869', 6528.3419565173335, 14765082.756849209], [u'hdc2383', 367260.47592005413, 5788626438.1929483], [u'cps1160', 252868.13608286722, 884819397.36503839], [u'swh0955', 830636.94363810716, 706437579.36770582], [u'swh0918', 1472638.4807493303, 6217391680.3640585]]
# 2008 match data
frw_y2matchdata = [[u'nps1387', 391810.93579751794, 1711787273.5598774], [u'sjs2742', 0.0, 0.0], [u'nps1433', 310158.22380991612, 595748883.00832057], [u'nps1328', 267365.24879528332, 3988164714.8396354], [u'hdc2283', 924844.61956966901, 13203803928.720116], [u'hdc2284', 1030121.7722244665, 8875346586.0276794], [u'swh0881', 0.0, 0.0], [u'swh0869', 8166.2397642551814, 6070942.5022775074], [u'hdc2383', 461831.29724269669, 7079312762.6476727], [u'cps1160', 214160.87377709564, 929840467.35095119], [u'swh0955', 885493.30819616525, 2193937155.4220476], [u'swh0918', 1599381.5539709965, 9880620715.7350445]]

# Creates the comma-delimited output string 
#  using formatting based on object type 
def output_string(v1,*vals):
    out_string = "%s" % v1
    for v in vals:
        if type(v) == str or type(v) == unicode:
            out_string = out_string + ",%s" % v
        elif type(v) == int:
            out_string = out_string + ",%i" % v
        else:
            out_string = out_string + ",%r" % v
    out_string = out_string + "\n"
    return out_string

def bootstrap(data):
    new_data = copy.deepcopy(data)
    # Randomly select members from a sample (with replacement)
    # This simulates sampling error
    #bootstrap_data = [random.choice(new_data) for i in range(len(data))]  # sites duplicated - need a copy
    bootstrap_data = []
    for i in xrange(len(data)):
        mychoice = random.choice(new_data)
        try:
            # If site already exists in bootstrap sample, make a copy to add
            bootstrap_data.index(mychoice)
            bootstrap_data.append(mychoice[:])
        except:
            # If site doesn't already exist in bootstrap sample, just add it
            bootstrap_data.append(mychoice)
    return bootstrap_data

def match_sites(data1,data2):
    # Find the data from the year 2 that match the new, bootstrapped year 1 data
    #data2_copy = copy.deepcopy(data2)
    data2_match = []
    for site in data1:
        site_id = site[0]
        for site in data2:
            try:
                site.index(site_id)
                data2_match.append(site[:])
                break
            except:
                continue
    return data2_match


def measurement_error(data,i,grp):
    # Simulate measurement error in the Zm Area estimate
    # using the variance and a random number
    newdata = copy.deepcopy(data)
    #print "before measurement error:"
    #print data
    #print newdata
    for site in newdata:
        siteid = site[0]
        zmArea = site[1]
        zmAreaVar = site[2]
        randNum = random.normalvariate(0,1)
        #print "------------------------------"
        #print "Site %s" % site[0]
        #print "Random Number %r" % randNum
        #print "Z marina original area %r:" % zmArea
        #print "Z marina variance %r" % zmAreaVar
        #print "Z marina standard error %r" % (zmAreaVar ** 0.5)
        #print "Error to add to Zm area %r" % ((zmAreaVar ** 0.5) * randNum)
        se = zmAreaVar ** 0.5
        sim_zmArea = zmArea + (se * randNum)
        # If area ends up less than zero, change it to zero
        if sim_zmArea < 0:
            sim_zmArea = 0
        site[1] = sim_zmArea
        print_string = output_string(i,grp,siteid,zmArea,zmAreaVar,se,randNum,(se * randNum),sim_zmArea)
        outFileSiteMC.write(print_string)
    #print "after measurement error"
    #print data
    #print newdata
    return newdata

def conf_int(rel_changes,pct_ci):
    # Takes a list of relative change values
    # and finds the mean and the 95% confidence interval
    mean_rc = sum(rel_changes) / len(rel_changes)
    #sort_rcs = sorted(rel_changes[:])
    #print rel_changes
    #print sort_rcs
    #conf_intervals = [abs(mean_rc - v) for v in sort_rcs]
    conf_intervals = [abs(mean_rc - rc) for rc in rel_changes]
    #print conf_intervals
    cis_sorted = sorted(conf_intervals)
    #print cis_sorted
    #print len(cis_sorted)
    idx_ci = int(len(cis_sorted) * pct_ci)
    #print count_ci
    #print cis_sorted[(idx_ci - 1)]
    #print cis_sorted[idx_ci]
    #print (cis_sorted[(idx_ci - 1)] + cis_sorted[idx_ci]) / 2
    ci = (cis_sorted[(idx_ci - 1)] + cis_sorted[idx_ci]) / 2
    return ci


rel_changes = []
# ----- Do 20000 iterations -----
def all_steps():
    print time.asctime()
    iterations = 20000
    sum_rc = 0
    for i in range(iterations):
        # Sampling Error
        bs1 = svmp.bootstrap(frw_sitedata)
        bs1m = svmp.bootstrap(frw_y1matchdata)
        bs2m = svmp.match_sites(bs1m,frw_y2matchdata)
        # Measurement Error
        me1 = svmp.measurement_error(bs1,i,"y1",outFileSiteMC)
        me1m = svmp.measurement_error(bs1m,i,"y1match",outFileSiteMC)
        me2m = svmp.measurement_error(bs2m,i,"y2match",outFileSiteMC)
        #me1 = svmp.measurement_error(bs1,i,"y1")
        #me1m = svmp.measurement_error(bs1m,i,"y1match")
        #me2m = svmp.measurement_error(bs2m,i,"y2match")
        # Calculate Change Analysis stats with Simulated Data
        yr1Samp  = svmp.SampleStats(me1,frwStratum,unit_convert)
        yr1mSamp = svmp.SampleStats(me1m,frwStratum,unit_convert)
        yr2mSamp = svmp.SampleStats(me2m,frwStratum,unit_convert)  
        frwChange = svmp.ChangeStats(yr1mSamp,yr2mSamp,yr1Samp)
        rc = frwChange.change_prop
        #print "Relative Change %r" % rc
        rcString = "%i,%r\n" % (i,rc)
        #print rcString
        rel_changes.append(rc)
        #sum_rc = sum_rc + rc
        outFileRC.write(rcString)
        
    mean_rc = sum(rel_changes)/ iterations
    print "Mean Relative Change %r" % mean_rc
    conf95pct = svmp.conf_int(rel_changes,0.95)
    print "95 percent confidence interval %r" % conf95pct
    print time.asctime()

outFileSiteMC = open(outFilenameSiteMC,'w')
outFileRC = open(outFilenameRC,'w')
frwStratum = svmp.FringeStratum(svmp.fr_extrap[0],svmp.fr_extrap[1],gp,fringeFC,unit_convert)

all_steps()

outFileSiteMC.close()
outFileRC.close()
