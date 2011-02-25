import svmpUtils
import math

# Map Geo and Sampling stratum to analysis stratum and extrapolation type
# This one is used for Area calculations where Persistent flats are reported
# separately from core sites
#(stratum_geo,stratum_samp) : (stratum_analysis,extrapolation)
stratum4AreaCalcs ={
("frw","core"):("core","none"),
("fr","core"):("core","none"),
("fl","core"):("core","none"),
("fl","persistent"):("persistent flats","none"),
("fl","rotational"):("flats","area"),
("fr","rotational"):("fringe","linear"),
("frw","rotational"):("wide fringe","linear")
}
# This one is used for Area Change calculations where Persistent flats are reported
# together with core sites
stratum4AreaChgCalcs ={
("frw","core"):("core","none"),
("fr","core"):("core","none"),
("fl","core"):("core","none"),
("fl","persistent"):("core","none"),
("fl","rotational"):("flats","area"),
("fr","rotational"):("fringe","linear"),
("frw","rotational"):("wide fringe","linear")
}

     
class Site(object):
    """ represents the SVMP data for an individual site
    attributes: siteid, ZmArea, ZmAreaVar, stratum_geo, stratum_samp
    optional -- aj (sample area for rotational flats) """
    
    def __init__(self, (siteid, siteZmArea, siteZmAreaVar, stratum_geo, stratum_samp)):
        self.siteid = siteid
        self.siteZmArea = siteZmArea
        self.siteZmAreaVar = siteZmAreaVar
        self.stratum_geo = stratum_geo
        self.stratum_samp = stratum_samp

    def __repr__(self):
        return repr((self.siteid,self.siteZmArea,self.siteZmAreaVar,self.stratum_geo,self.stratum_samp))

class BaseStratum(object):
    """ represents an analysis stratum for grouping of SVMP sites 
    attributes: geo, samp, analysis, extrapolation""" 
    
    def __init__(self,geo,samp,analysis,extrapolation):
        self.geo = geo
        self.samp = samp
        self.analysis = analysis
        self.extrapolation = extrapolation
    
    # Not sure reason to do it this way:
    #def __init__(self,*args):
        #self.geo = args[0]
        #self.samp = args[1] 
        #self.analysis = args[2]
        #self.extrapolation = args[3]
    
class FlatsStratum(BaseStratum):
    """ Constants associated with Rotational Flats Stratum """
    """ Subclass of BaseStratum """
    def __init__(self,geo,samp,analysis,extrapolation):
        BaseStratum.__init__(self,geo,samp,analysis,extrapolation)
        self.Ni = 66
        self.A2 = 323000000 / svmpUtils.sf2_m2
        self.Aij = 55559000 / svmpUtils.sf2_m2

        
class FringeStratum(BaseStratum):
    """ Constants associated with Fringe (Regular and Wide) Strata """
    """ Subclass of BaseStratum """
    def __init__(self,geo,samp,analysis,extrapolation):
        BaseStratum.__init__(self,geo,samp,analysis,extrapolation)
        # These are dummy numbers for now
        self.Ni = 20355
        self.LT = 2095990
        self.LN = self.Ni * 1000 / svmpUtils.sf_m
    
class Sample(object):
    """ represents a sample of SVMP sites """
    """ A sample has sites and a stratum """
    """ Attributes:
    sites -- a list of site objects
    stratum  -- a stratum object
    extrapolation -- extrapolation type (none,linear, area)
    ni -- count of sites in sample
    siteids - list of individual site ids in sample
    zmareas -- list of individual site Zm Area values
    zmvars -- list of individual site Zm Variance values
    ZmArea -- Estimated Zm Area for the Sample (based on extrapolation type)
    ZmAreaVar -- Estimated Zm Area Variance for the Sample (based on extrapolation type)
    SE -- Standard Error (same for all extrapolation types)
    CV -- Coefficient of variation (same for all extrapolation types)  
    """
    sites = [] # SITE OBJECTS TO BE
    stratum = None
    extrapolation = None
    
    def __init__(self,sites_list,stratum=None):
        self.importSites(sites_list) 
        self.ni = self.countSites()  # why does this return 0?
        self.countSites() # Site count
        self.setSiteids() # List of Site IDs
        self.setZmAreas() # List of Site Zm Areas
        self.setZmVars() # List of Site Zm Area Variances
        if stratum:
            self.addStratum(stratum)

    def __repr__(self):
        return repr(self.sites)
        
    def importSites(self,sites_list):
        """Create Site objects from a list of site data """
        """ Append these sites objects to a sample """ 
        self.sites = []
        for s in sites_list:
            mySite = Site(s)
            self._addSite(mySite)
    
    def _addSite(self,site):
        """ Adds individual site objects to the sample """
        self.sites.append(site)
    
    def setSiteids(self):
        """ Creates a list of the sample's site ids """
        self.siteids = []
        for site in self.sites:
            self.siteids.append(site.siteid)
    
    def setZmAreas(self):
        """ Creates a list of the sample's site ZM areas"""
        self.zmareas = []
        for site in self.sites:
            self.zmareas.append(site.siteZmArea)
            
    def setZmVars(self):
        """ Creates a list of the sample's site ZM area variances """
        self.zmvars = []
        for site in self.sites:
            self.zmvars.append(site.siteZmAreaVar)
        
    def addStratum(self,stratum):
        """ Adds a stratum object to the sample """
        self.stratum = stratum
        self.extrapolation = self.stratum.extrapolation
        # self.stratum_analysis = self.stratum.analysis # may not need as attribute of Sample
        # Which method is preferred?
        #self.stratum_analysis = stratum.analysis
        #self.extrapolation = stratum.extrapolation

    def calcZmArea(self):
        """ Calculate Area of Zostera marina based on extrapolation type """
        #-- NO EXTRAPOLATION
        if self.extrapolation == "none":
            self.ZmArea = sum(self.zmareas)
        #-- AREA EXTRAPOLATION
        if self.extrapolation == "area":
            self.ZmArea = sum(self.zmareas) * self.stratum.A2 / self.stratum.Aij
        #-- LINEAR EXTRAPOLATION
        if self.extrapolation == "linear":
            self.ZmArea = self.stratum.LT / self.stratum.LN * self.meanZmArea() * self.stratum.Ni
        return self.ZmArea

    def calcZmAreaVar(self):
        """ Calculate Variance of Zostera marina Area based on extrapolation type """
        #-- NO EXTRAPOLATION
        if self.extrapolation == "none":
            self.ZmAreaVar = sum(self.zmvars)
        #-- AREA EXTRAPOLATION
        if self.extrapolation == "area":
            self.ZmAreaVar = 0
        #-- LINEAR EXTRAPOLATION
        if self.extrapolation == "linear":
            self.ZmAreaVar = ( (self.stratum.LT / self.stratum.LN) ** 2 ) * (((self.stratum.Ni ** 2) * (1 - self.ni / self.stratum.Ni) * self.variance()) / self.ni) + ((self.stratum.Ni / self.ni) * sum(self.zmvars))
        return self.ZmAreaVar

    def calcSE(self):
        """ Calculate the Standard Error """
        # Make sure the Variance is already calculated
        if not hasattr(self,'ZmAreaVar'):
            self.calcZmAreaVar()
        # Standard Error = Square Root of Variance
        self.SE = self.ZmAreaVar ** 0.5
        # Should I be returning the value also?
        # Or just setting the attribute?
        return self.SE
        
    def calcCV(self):
        """ calculate the coefficient of variation """
        # Make sure Zm Area and Standard Error are already calculated
        if not hasattr(self,'ZmArea'):
            self.calcZmArea()
        if not hasattr(self,'SE'):
            self.calcSE()
        # Coefficient of Variation = Standard Error / Zm Area
        if self.ZmArea > 0:
            self.CV = self.SE / self.ZmArea
        else:
            self.CV = 0
        return self.CV
        
    def countSites(self):
        """ count the number of sites in a sample """
        self.ni = len(self.sites)
        return self.ni
    
    def meanZmArea(self):
        """ Mean Z marina area for the Sample"""
        sumArea = 0
        for site in self.sites:
            sumArea = sumArea + site.siteZmArea
        meanArea = sumArea / self.countSites()
        return meanArea
    
    def variance(self):
        """ Variance of Sample's Zm site areas """
        sum_sqdif = 0 # initialize sum of squared differences
        # Calculate sum of squared differences
        for site in self.sites:
            sqdif = (site.siteZmArea - self.meanZmArea()) ** 2
            sum_sqdif = sqdif + sum_sqdif  
        # Standard Deviation
        stddev = ((1 / ( float(self.ni) - 1 )) * sum_sqdif ) ** 0.5
        # Variance
        var = stddev ** 2
        return var

class AnnualEstimates(object):
    """ represents the annual Zmarina area estimates and error estimates"""
    """ Attributes:
    ZmArea -- Estimated Zm Area for the Sample (based on extrapolation type)
    ZmAreaVar -- Estimated Zm Area Variance for the Sample (based on extrapolation type)
    SE -- Standard Error (same for all extrapolation types)
    CV -- Coefficient of variation (same for all extrapolation types)      
    """
    def __init__(self,samples):
        self.samples = samples
        self.setZmVars()
        self.setZmAreas()
        self.calcZmArea()
        self.calcZmAreaVar()
        self.calcSE()
        self.calcCV()

    def __repr__(self):
        return repr((self.ZmArea,self.ZmAreaVar,self.SE,self.CV))
    
    def setZmAreas(self):
        """ Creates a list of estimated Zm area from each sample (stratum) """
        self.zmareas = []
        for sample in self.samples:
            self.zmareas.append(sample.ZmArea)

    def setZmVars(self):
        """ Creates a list of estimatedZM area variances from each sample (stratum)"""
        self.zmvars = []
        for sample in self.samples:
            self.zmvars.append(sample.ZmAreaVar)
            
    def calcZmArea(self):
        self.ZmArea = sum(self.zmareas)
        
    def calcZmAreaVar(self):
        self.ZmAreaVar = sum(self.zmvars)
        
    def calcSE(self):
        """ Calculate the Standard Error """
        # Make sure the Variance is already calculated
        if not hasattr(self,'ZmAreaVar'):
            self.calcZmAreaVar()
        # Standard Error = Square Root of Variance
        self.SE = self.ZmAreaVar ** 0.5
        # Should I be returning the value also?
        # Or just setting the attribute?
        return self.SE
        
    def calcCV(self):
        """ calculate the coefficient of variation """
        # Make sure Zm Area and Standard Error are already calculated
        if not hasattr(self,'ZmArea'):
            self.calcZmArea()
        if not hasattr(self,'SE'):
            self.calcSE()
        # Coefficient of Variation = Standard Error / Zm Area
        if self.ZmArea > 0:
            self.CV = self.SE / self.ZmArea
        else:
            self.CV = 0
        return self.CV
    


