import svmp_93 as svmp
import arcgisscripting


gp = arcgisscripting.create(9.3)

## Parameters
dbPath = "C:/projects/dnr_svmp/dnr_data/fromDNR_20100806/"
blPath = "c:/projects/dnr_svmp/dnr_data/fromDNR_20100806/baselayers/"
outPath = "c:/projects/dnr_svmp/output/eelgrass_monitoring/ab_out/"
siteTable = dbPath  + "svmp_sitesdb_2009_ab.mdb/all_years_sites_ab" 
allsitesFC = blPath + "svmp_all_sites_ab.shp"
flatsFC = blPath + "flats.shp"
fringeFC = blPath + "fringe.shp"
year1 = 2008
year2 = 2009
sample_group = "soundwide"   # placeholder -- may be implemented as a parameter later (for soundwide, focus and other sites)
unit_convert = "sf2m"   # unit conversion flag

class ChangeStatsTest(object):
    """ Represents the Statistics for Year-to-Year Change Analysis for a Stratum
    
    A ChangeStats object has three Samples:
    Samples y1m and y2m contain the matching sites sampled in both years
    Sample y1 contains all the sites sampled in Year 1
    
    """
    def __init__(self,data_y1m,data_y2m):
        self.xs = data_y1m
        self.ys = data_y2m
        self.x2sum = self.sum_of_squares(self.xs)
        self.y2sum = self.sum_of_squares(self.ys)
        self.xysum = self.sum_xy()
        self.m = self.slope()
        self.m_se = self.se_slope()
    
    
    def sum_of_squares(self,vals):
        """ Sum of the individual squared ZM areas in a sample """
        val2 = [v ** 2 for v in vals]
        return sum(val2)
    
    def sum_xy(self):
        """ Sum of the product of matching Zm areas for two different years """
        xy = []
        for (x,y) in zip(self.xs,self.ys):
            xy.append(x * y)
        return sum(xy)
    
    def slope(self):
        """ Slope of the regression line for two years ZM Areas
            Line goes through origin
            If the sum of the xy-product is zero, the slope will be zero
        """
        if self.xysum == 0:
            return 0
        else:
            return float(self.xysum) / self.x2sum
    
    def se_slope(self):
        """ Calculate standard error of the slope """
        #slope_var = ((self.y2sum - (self.xysum ** 2) / self.x2sum) / (len(self.xs) - 1)) / self.x2sum # current code
        
        if self.xysum == 0:
            slope_var = 0
        else:
            slope_var = ((self.y2sum - (self.xysum ** 2 / self.x2sum)) / (len(self.xs) - 1)) / self.x2sum # matches parens in PD excel sheet -- same result
            part1 = self.xysum ** 2 / self.x2sum
            print part1
            part2 = self.y2sum - part1
            print part2
            part3 = len(self.xs) - 1
            print part3
            part4 = part2 / part3
            print part4
            part5 = part4 / self.x2sum
            print part5
        
        print self.xs
        print self.ys
        print self.x2sum
        print self.y2sum
        print self.xysum
        print self.m
        
        print slope_var
        if slope_var < 0:
            slope_var = abs(slope_var)
        print slope_var ** 0.5
        return slope_var ** 0.5
    
    def proportion_change(self):
        """ The proportion change of Zm area between two years
            referred to as percent change, but proportion is used in equations"""
        return self.m - 1
    


# SIMULATED SAMPLE DATA
# 2008 all data
frw_sitedata = [[u'nps1433', 341838.203859, 595748865.340163], [u'cps1160', 219209.328729, 929840494.085674], [u'nps1328', 362154.50736, 3988164685.39394], [u'sjs2742', 0.0, 0.0], [u'nps1433', 303028.637587, 595748865.340163], [u'nps1387', 405867.69473, 1711787198.98744], [u'cps1160', 222858.329851, 929840494.085674], [u'swh0918', 1711780.88333, 9880620586.57411], [u'hdc2383', 537126.386446, 7079312539.13064], [u'swh0882', 0.0, 0.0], [u'swh0882', 0.0,0.0], [u'sjs2742', 0.0, 0.0],  [u'sjs2742', 0.0, 0.0]]
# 2008 match data
frw_y1matchdata = [[u'sjs2742', 0.0, 0.0], [u'swh0881', 0.0, 0.0], [u'swh0955', 906876.141151, 2193937179.89847], [u'swh0882', 0.0, 0.0], [u'sjs2742', 0.0, 0.0], [u'swh0882', 0.0, 0.0], [u'swh0881', 0.0, 0.0], [u'swh0882', 0.0, 0.0],[u'sjs2742', 0.0, 0.0],[u'sjs2742', 0.0, 0.0]]
# 2008 match data
frw_y2matchdata = [[u'sjs2742', 0.0, 0.0], [u'swh0881', 0.0, 0.0], [u'swh0955', 1109013.57607, 1643674966.8892], [u'swh0882', 0.0, 0.0], [u'sjs2742', 0.0, 0.0], [u'swh0882', 0.0, 0.0], [u'swh0881', 0.0, 0.0], [u'swh0882', 0.0, 0.0],[u'sjs2742', 0.0, 0.0],[u'sjs2742', 0.0, 0.0]]

# Try with all zeroes
# 2008 match data
frw_y1matchdata = [[u'sjs2742', 0.0, 0.0], [u'swh0881', 0.0, 0.0], [u'swh0955', 0.0, 0.0], [u'swh0882', 0.0, 0.0], [u'sjs2742', 0.0, 0.0], [u'swh0882', 0.0, 0.0], [u'swh0881', 0.0, 0.0], [u'swh0882', 0.0, 0.0],[u'sjs2742', 0.0, 0.0],[u'sjs2742', 0.0, 0.0]]
# 2008 match data
frw_y2matchdata = [[u'sjs2742', 0.0, 0.0], [u'swh0881', 0.0, 0.0], [u'swh0955', 0.0, 0.0], [u'swh0882', 0.0, 0.0], [u'sjs2742', 0.0, 0.0], [u'swh0882', 0.0, 0.0], [u'swh0881', 0.0, 0.0], [u'swh0882', 0.0, 0.0],[u'sjs2742', 0.0, 0.0],[u'sjs2742', 0.0, 0.0]]



def test1():
    #stratum object
    frwStratum = svmp.FringeStratum(svmp.frw_extrap[0],svmp.frw_extrap[1],gp,fringeFC,unit_convert)
    print frwStratum
    
    yr1Samp  = svmp.SampleStats(frw_sitedata,frwStratum,unit_convert)
    print yr1Samp.zm_area, yr1Samp.zm_area_var,yr1Samp.cv,yr1Samp.se
    
    yr1mSamp = svmp.SampleStats(frw_y1matchdata,frwStratum,unit_convert)
    print yr1mSamp.zm_area, yr1mSamp.zm_area_var,yr1mSamp.cv,yr1mSamp.se
    
    yr2mSamp = svmp.SampleStats(frw_y2matchdata,frwStratum,unit_convert)
    print yr2mSamp.zm_area, yr2mSamp.zm_area_var,yr2mSamp.cv,yr2mSamp.se
    
    frwChange = svmp.ChangeStats(yr1mSamp,yr2mSamp,yr1Samp)
    print frwChange.xs
    print frwChange.ys
    print frwChange.x2sum
    print frwChange.xysum
    print frwChange.y2sum
    print frwChange.m
    print frwChange.m_se

# Full program is bombing out on these
sample_xs = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 92816.781168511923, 0.0, 0.0]
sample_ys = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 80133.309326454531, 0.0, 0.0]

sample_xs = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0]
sample_ys = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0]


def test2():
    test = ChangeStatsTest(sample_xs,sample_ys)
    
#test2()
test1()