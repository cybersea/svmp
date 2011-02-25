"""Major Classes and Data Structures for the SVMP Tools Module."""

import svmpUtils
import math


# Map Geo and Sampling stratum to analysis stratum and extrapolation type
# This one is used for Area calculations where Persistent flats are reported
# separately from core sites

core_extrap = ("core","none")
pfl_extrap = ("persistent flats","none")
fl_extrap = ("flats","area")
fr_extrap = ("fringe","linear")
frw_extrap = ("wide fringe","linear")

#(stratum_geo,stratum_samp) : (stratum_analysis,extrapolation)
sw_Stratum4AreaCalcs ={
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
sw_Stratum4AreaChgCalcs ={
("frw","core"):("core","none"),
("fr","core"):("core","none"),
("fl","core"):("core","none"),
("fl","persistent"):("core","none"),
("fl","rotational"):("flats","area"),
("fr","rotational"):("fringe","linear"),
("frw","rotational"):("wide fringe","linear")
}

     
class Site(object):
    """ Represents the SVMP data for an individual site.
    
    Attributes:
    siteid -- individual site identifier
    zmArea -- site Zm area
    zmAreaVar -- site Zm area variance
    
    optional -- aj (sample area for rotational flats)
    
    """
    def __init__(self,site_data,conversion=None):
        # this seems a little kludgy -- prefer to have the parameters named on command line,
        #  but it would not let me have an optional parameter in the tuple:  (self,(id,zmArea,zmAreaVar,aj=None),conversion=None)
        self.id = site_data[0]
        self.zmArea = site_data[1]
        self.zmAreaVar = site_data[2]
        if len(site_data) == 4:
            self.aj = site_data[3]
        # Convert units if necessary
        if conversion:
            self.convert_units(conversion)
                               
    def __repr__(self):
        return repr((self.id,self.zmArea,self.zmAreaVar))
    
    def convert_units(self,conversion):
        if conversion == "sf2m":
            self.zmArea = self.zmArea * (svmpUtils.sf_m ** 2)
            self.zmAreaVar = self.zmAreaVar * (svmpUtils.sf_m ** 4)
            if hasattr(self,'aj'):
                self.aj = self.aj * (svmpUtils.sf_m ** 2)
        else:
            err_text = "Conversion type, %s, is not available" % conversion
            raise ValueError(err_text)
        
    
class BaseStratum(object):
    """ Represents an analysis stratum for grouping of SVMP sites.
     
    Attributes:
    geo, samp, analysis, extrapolation
    
    """ 
    def __init__(self,analysis,extrapolation):
        self.analysis = analysis
        self.extrapolation = extrapolation
    
class FlatsStratum(BaseStratum):
    """ Constants associated with Rotational Flats Stratum.
    
    Subclass of BaseStratum
    
    """
    def __init__(self,analysis,extrapolation):
        BaseStratum.__init__(self,analysis,extrapolation)
        self.Ni = 66
        self.A2 = 323000000  / svmpUtils.sf2_m2
        self.Aij = 55559000 / svmpUtils.sf2_m2

        
class FringeStratum(BaseStratum):
    """Constants associated with Fringe (Regular and Wide) Strata.
    
    Subclass of BaseStratum
    
    """
    def __init__(self,analysis,extrapolation):
        BaseStratum.__init__(self,analysis,extrapolation)
        # These are dummy numbers for now
        self.Ni = 2035
        self.LT = 2095990
        self.LN = self.Ni * 1000 / svmpUtils.sf_m
    
class Sample(object):
    """ Represents a sample of SVMP sites.
    
    A sample has sites and a stratum.
    
    Attributes:
    sites -- a list of site objects
    stratum  -- a stratum object
    ni -- count of sites in sample
    site_ids - list of individual site ids in sample
    zm_areas -- list of individual site Zm Area values
    zm_vars -- list of individual site Zm Variance values
    zm_area -- Estimated Zm Area for the Sample (based on extrapolation type)
    zm_area_var -- Estimated Zm Area Variance for the Sample (based on extrapolation type)
    se -- Standard Error (same for all extrapolation types)
    cv -- Coefficient of variation (same for all extrapolation types)
    meanZmArea -- Mean Zm Area for the Sample
    variance -- Variance of the Sample's Zm site areas
    
    Example Doctest:
    >>> site1 = ["core001",318285957.367152,7.81016158406864E+14,"fl","core"]
    >>> site2 = ["core002",244910.733927743,364666178.032925,"fl","core"]
    >>> frSamp = Sample([site1,site2])
    >>> frSamp.sites[1]
    ('core002', 244910.73392774299, 364666178.03292501, 'fl', 'core')
    >>> frSamp.sites[1].siteid
    'core002'
    >>> len(frSamp.sites)
    2
    >>> frSamp.ni
    2
    >>> frSamp.countSites()
    2
    >>> frSamp.ni
    2
    
    """    
    def __init__(self,sites_list,stratum,conversion=None):
        """ Create a Sample from a list of sites. """
        self.sites = []
        self.conversion = conversion
        self.importSites(sites_list) 
        self.set_stratum(stratum)

    def __repr__(self):
        return repr(self.sites)
        
    def importSites(self,sites_list):
        """Create Site objects from a list of site data.
        
        Append these sites objects to a sample
        
        """ 
        for s in sites_list:
            mySite = Site(s,self.conversion)
            self._addSite(mySite)
    
    def _addSite(self,site):
        """ Adds individual site objects to the sample. """
        self.sites.append(site)

    def set_stratum(self,stratum):
        """ Sets the stratum object for the sample """
        self.stratum = stratum
        
    def _site_attrs(self,attr):
        return [getattr(site,attr) for site in self.sites]

    @property
    def site_ids(self):
        """ Fetch the list of the sample's site ids.
        
        Note: the @property decorator allows for the 
        method to behave like a 'read-only' attribute
        so you can do something cleanly like:
        
        >>> s = Sample()
        >>> s.site_ids
        []
        
        """
        return self._site_attrs('id')
    
    @property
    def zm_areas(self):
        """ Fetch a list of the sample's site ZM areas """
        return self._site_attrs('zmArea')

    @property
    def zm_vars(self):
        """ Fetch a list of the sample's site ZM area variances """
        return self._site_attrs('zmAreaVar')
        
    ## ***NOTE*** Dane got to here and no farther in initial code review...

    @property
    def zm_area(self):
        """ Calculate Area of Zostera marina based on extrapolation type """
        #-- NO EXTRAPOLATION
        if self.stratum.extrapolation == "none":
            zmArea = sum(self.zm_areas)
        #-- AREA EXTRAPOLATION
        if self.stratum.extrapolation == "area":
            zmArea = sum(self.zm_areas) * self.stratum.A2 / self.stratum.Aij
        #-- LINEAR EXTRAPOLATION
        if self.stratum.extrapolation == "linear":
            zmArea = self.stratum.LT / self.stratum.LN * self.meanZmArea * self.stratum.Ni
        return zmArea
    
    @property
    def zm_area_var(self):
        """ Calculate Variance of Zostera marina Area based on extrapolation type """
        #-- NO EXTRAPOLATION
        if self.stratum.extrapolation == "none":
            zmAreaVar = sum(self.zm_vars)
        #-- AREA EXTRAPOLATION
        if self.stratum.extrapolation == "area":
            zmAreaVar = 0 #(self.stratum.Ni ** 2) * (1 - self.ni/self.stratum.Ni)#0  #placeholder
        #-- LINEAR EXTRAPOLATION
        if self.stratum.extrapolation == "linear":
            zmAreaVar = ( (self.stratum.LT / self.stratum.LN) ** 2 ) * (((self.stratum.Ni ** 2) * (1 - self.ni / self.stratum.Ni) * self.variance()) / self.ni) + ((self.stratum.Ni / self.ni) * sum(self.zm_vars))
        return zmAreaVar
    
    @property
    def se(self):
        """ Calculate the Standard Error """
        # Standard Error = Square Root of Variance
        return self.zm_area_var ** 0.5
    
    @property
    def cv(self):
        """ Calculate the coefficient of variation """
        # Coefficient of Variation = Standard Error / Zm Area
        return self.se / self.zm_area

    @property 
    def ni(self):
        return len(self.sites)
        
    @property
    def meanZmArea(self):
        """ Mean Z marina area for the Sample"""
        sumArea = 0
        for site in self.sites:
            sumArea = sumArea + site.zmArea
        meanArea = sumArea / self.ni
        return meanArea
    
    def variance(self):
        """ Variance of Sample's Zm site areas """
        sum_sqdif = 0 # initialize sum of squared differences
        # Calculate sum of squared differences
        for site in self.sites:
            sqdif = (site.zmArea - self.meanZmArea) ** 2
            sum_sqdif = sqdif + sum_sqdif  
        # Standard Deviation
        stddev = ((1 / ( float(self.ni) - 1 )) * sum_sqdif ) ** 0.5
        # Variance
        var = stddev ** 2
        return var
        

class AnnualEstimate(object):
    """ Represents the annual Zmarina area estimate and associated error estimates.
    
    An annual estimate has a list of Sample objects 
    
    Attributes:
    zm_areas -- list of all Sample estimated areas
    zm_vars -- list of all Sample estimated variances
    zm_area -- Estimated Zm Area for the Annual Estimate
    zm_area_var -- Estimated Zm Area Variance for the Annual Estimate
    se -- Standard Error 
    cv -- Coefficient of variation      
    
    """
    def __init__(self,samples):
        self.samples = samples

    def __repr__(self):
        return repr((self.zm_area,self.zm_area_var,self.se,self.cv))
    
    def _sample_attrs(self,attr):
        return [getattr(sample,attr) for sample in self.samples]

    @property
    def zm_areas(self):
        """ Fetch a list of the sample's site ZM areas """
        return self._sample_attrs('zm_area')

    @property
    def zm_vars(self):
        """ Fetch a list of the sample's site ZM area variances """
        return self._sample_attrs('zm_area_var')
    
    @property
    def zm_area(self):
        """ Calculate Area of Zostera marina by summing Sample areas """
        return sum(self.zm_areas)
    
    @property
    def zm_area_var(self):
        """ Calculate Variance of Zostera marina Area by summing Sample variances"""
        return sum(self.zm_vars)
    
    @property
    def se(self):
        """ Calculate the Standard Error """
        # Standard Error = Square Root of Variance
        return self.zm_area_var ** 0.5
    
    @property
    def cv(self):
        """ Calculate the coefficient of variation """
        # Coefficient of Variation = Standard Error / Zm Area
        return self.se / self.zm_area
    

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True,report=True)