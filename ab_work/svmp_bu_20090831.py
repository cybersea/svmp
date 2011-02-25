"""Major Classes and Data Structures for the SVMP Tools Module."""

import svmpUtils
import math
import svmp_spatial as spatial


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
    zmAreaVar -- site Zm area variance (optional)
    
    optional -- a2j (sample area for rotational flats)
    
    """
    def __init__(self,id,zmArea,zmAreaVar,a2j=None,conversion=None):
        # is this less kludgy?
        self.id = id
        self.zmArea = zmArea
        self.zmAreaVar = zmAreaVar
        self.a2j = a2j
        
#    def __init__(self,site_data,conversion=None):
#        self.id = site_data[0]
#        self.zmArea = site_data[1]
#        self.zmAreaVar = site_data[2]
#        if len(site_data) == 4:
#            self.aj = site_data[3]

        # Convert units if necessary
        if conversion:
            self.convert_units(conversion)
                               
    def __repr__(self):
        return repr((self.id,self.zmArea,self.zmAreaVar))
    
    def convert_units(self,conversion):
        # should this return something?
        if conversion == "sf2m":
            self.zmArea = self.zmArea * (svmpUtils.sf_m ** 2)
            self.zmAreaVar = self.zmAreaVar * (svmpUtils.sf_m ** 4)
            if self.a2j:
                self.a2j = self.a2j * (svmpUtils.sf_m ** 2)
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
    def __init__(self,analysis,extrapolation,gp,stratum_fc,conversion=None):
        BaseStratum.__init__(self,analysis,extrapolation)
        
        self.gp = gp
        self.stratum_fc = stratum_fc
        self.conversion = conversion
        self.query_string = '"NAME" <> \'\' and "focus_stra" not in (\'c\',\'pfl\')'
        
        self.Ni = self.get_Ni()
        self.A2 = self.get_A2()

    def get_Ni(self):
        """ count the number of rotational flats in the stratum """
        qry = spatial.FeatureQuery(self.gp,self.stratum_fc,self.query_string)
        count = qry.record_count
        del qry
        return count
        
    def get_A2(self):
        """ get the sum of the rotational flats stratum area """
        qry = spatial.FeatureQuery(self.gp,self.stratum_fc,self.query_string)
        if self.conversion:
            if self.conversion == "sf2m":
                area = qry.geometry_sum * (svmpUtils.sf_m ** 2)
            else:
                err_text = "Conversion type, %s, is not available" % conversion
                raise ValueError(err_text)
        else:
            area = qry.geometry_sum
        del qry
        return area

    #@property
    #def A2(self):
        #return self._A2 / svmpUtils.sf2_m2

    #@property
    #def Aij(self):
        #return self._Aij / svmpUtils.sf2_m2


        
class FringeStratum(BaseStratum):
    """Constants associated with Fringe (Regular and Wide) Strata.
    
    Subclass of BaseStratum
    
    """
    def __init__(self,analysis,extrapolation,gp,stratum_fc,conversion=None):
        BaseStratum.__init__(self,analysis,extrapolation)
        
        self.gp = gp # ESRI Geoprocessing object
        self.stratum_fc = stratum_fc # Feature class for queries
        self.conversion = conversion  # unit conversion flag
        self.Ni = self.get_Ni()
        self.LT = self.get_LT()
        self.LN = float(self.Ni) * 1000  # assumes output units are meters
        #self.Ni = 2035
        #self.LT = 2095990
        #self.LN = self.Ni * 1000 / svmpUtils.sf_m

        BaseStratum.__init__(self,analysis,extrapolation)
        
    def get_Ni(self):
        """ count the number of fringe sites in the stratum """
        # Query for the correct set of sites, based on analysis stratum
        if self.analysis == "fringe":
            query_string = '"2002TYPE" = \'fr\' and "REGION" <> \'sps\''
        elif self.analysis == "wide fringe":
            query_string = '"2002TYPE" = \'frw\' and "REGION" <> \'sps\''
        else:
            err_text = "Analysis stratum type, %s, is not a valid fringe stratum" % self.analysis
            raise ValueError(err_text)
        qry = spatial.FeatureQuery(self.gp,self.stratum_fc,query_string)
        count = qry.record_count
        del qry
        return count
       
    def get_LT(self):
        """ Sum of the Length of all fringe sites in the stratum """
        # Query for the correct set of sites, based on analysis stratum - includes "orphans"
        if self.analysis == "fringe":
            query_string = '"2002TYPE" in (\'fr\',\'fr-orphan<984m\') and "REGION" <> \'sps\''
            #query_string = '"2002TYPE" = \'fr\' or "2002TYPE" = \'fr-orphan<984m\' and "REGION" <> \'sps\''
        elif self.analysis == "wide fringe":
            query_string = '"2002TYPE" in (\'frw\',\'frw-orphan<984m\') and "REGION" <> \'sps\''
        else:
            err_text = "Analysis stratum type, %s, is not a valid fringe stratum" % self.analysis
            raise ValueError(err_text)
        # spatial query object
        qry = spatial.FeatureQuery(self.gp,self.stratum_fc,query_string)
        # Calculate total length, with unit conversion if necessary
        if self.conversion:
            if self.conversion == "sf2m":
                length = qry.geometry_sum * (svmpUtils.sf_m)
            else:
                err_text = "Conversion type, %s, is not available" % self.conversion
                raise ValueError(err_text)
        else:
            length = qry.geometry_sum
        del qry
        return length

    #def LN(self):
        #return float(self.Ni) * 1000

#class FlatsStratumConstants(object):
    #""" Represents the stratum constants for persistent flats,
    #extracted from shapefile baselayers
    #"""

    #def __init__(self,gp,stratum_fc,conversion=None):
        #self.gp = gp
        #self.stratum_fc = stratum_fc
        #self.conversion = conversion
        #self.query_string = '"NAME" <> \'\' and "focus_stra" not in (\'c\',\'pfl\')'
        #self.Ni = self.get_Ni()
        #self.A2 = self.get_A2()

    #def get_Ni(self):
        #""" count the number of rotational flats in the stratum """
        #qry = spatial.FeatureQuery(self.gp,self.stratum_fc,self.query_string)
        #count = qry.record_count
        #del qry
        #return count
        
    #def get_A2(self):
        #""" get the sum of the rotational flats stratum area """
        #qry = spatial.FeatureQuery(self.gp,self.stratum_fc,self.query_string)
        #if self.conversion:
            #if self.conversion == "sf2m":
                #area = qry.geometry_sum * (svmpUtils.sf_m ** 2)
            #else:
                #err_text = "Conversion type, %s, is not available" % conversion
                #raise ValueError(err_text)
        #else:
            #area = qry.geometry_sum
        #del qry
        #return area

#class FringeStratumConstants(object):
    #""" Represents the stratum constants for fringe sites,
    #extracted from shapefile baselayers
    #""" 
    #def __init__(self,analysis,gp,stratum_fc,conversion=None):
        #self.analysis = analysis
        #self.gp = gp
        #self.stratum_fc = stratum_fc
        #self.conversion = conversion
        ## Get the constants
        #self.Ni = self.get_Ni()
        #self.LT = self.get_LT()

    #def get_Ni(self):
        #""" count the number of fringe sites in the stratum """
        ## Query for the correct set of sites, based on analysis stratum
        #if self.analysis == "fringe":
            #query_string = '"2002TYPE" = \'fr\' and "REGION" <> \'sps\''
        #elif self.analysis == "wide fringe":
            #query_string = '"2002TYPE" = \'frw\' and "REGION" <> \'sps\''
        #else:
            #err_text = "Analysis stratum type, %s, is not a valid fringe stratum" % self.analysis
            #raise ValueError(err_text)
        #qry = spatial.FeatureQuery(self.gp,self.stratum_fc,query_string)
        #count = qry.record_count
        #del qry
        #return count
       
    #def get_LT(self):
        #""" Sum of the Length of all fringe sites in the stratum """
        ## Query for the correct set of sites, based on analysis stratum - includes "orphans"
        #if self.analysis == "fringe":
            #query_string = '"2002TYPE" in (\'fr\',\'fr-orphan<984m\') and "REGION" <> \'sps\''
            #query_string = '"2002TYPE" = \'fr\' or "2002TYPE" = \'fr-orphan<984m\' and "REGION" <> \'sps\''
        #elif self.analysis == "wide fringe":
            #query_string = '"2002TYPE" in (\'frw\',\'frw-orphan<984m\') and "REGION" <> \'sps\''
        #else:
            #err_text = "Analysis stratum type, %s, is not a valid fringe stratum" % self.analysis
            #raise ValueError(err_text)
        ## spatial query object
        #qry = spatial.FeatureQuery(self.gp,self.stratum_fc,query_string)
        ## Calculate total length, with unit conversion if necessary
        #if self.conversion:
            #if self.conversion == "sf2m":
                #length = qry.geometry_sum * (svmpUtils.sf_m)
            #else:
                #err_text = "Conversion type, %s, is not available" % self.conversion
                #raise ValueError(err_text)
        #else:
            #length = qry.geometry_sum
        #del qry
        #return length

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
        # import all the sites and set the stratum
        self.importSites(sites_list) 
        self.set_stratum(stratum)
        
        # Properties of the Sample
        # Lists of individual site values
        self.site_ids = self._site_attrs('id')
        self.zm_areas = self._site_attrs('zmArea')
        self.zm_vars = self._site_attrs('zmAreaVar')
        
    def __repr__(self):
        return repr(self.sites)
        
    def importSites(self,sites_list):
        """Create Site objects from a list of site data.
        
        Append these sites objects to a sample
        
        """ 
        for s in sites_list:
            args = s[:3]
            if len(s) == 4:
                a2j = s[3]
            else:
                a2j = None
            kwargs = {'a2j':a2j,'conversion':self.conversion}
            mySite = Site(*args,**kwargs)
            self._addSite(mySite)
    
    def _addSite(self,site):
        """ Adds individual site objects to the sample. """
        self.sites.append(site)

    def set_stratum(self,stratum):
        """ Sets the stratum object for the sample """
        self.stratum = stratum
        
    def _site_attrs(self,attr):
        return [getattr(site,attr) for site in self.sites]

    
class SampleStats(Sample):
    """ Represents a sample of SVMP sites with all the statistics as properties
    
    Subclass of Sample
        
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
        #self.sites = []
        #self.conversion = conversion
        ## import all the sites and set the stratum
        #self.importSites(sites_list) 
        #self.set_stratum(stratum)
        
        ## Properties of the Sample
        ## Lists of individual site values
        #self.site_ids = self._site_attrs('id')
        #self.zm_areas = self._site_attrs('zmArea')
        #self.zm_vars = self._site_attrs('zmAreaVar')
        
        Sample.__init__(self,sites_list,stratum,conversion=None)
        
        # Stats on entire Sample
        self.ni = len(self.sites)
        self.meanZmArea = self.meanZmArea(self.sites)
        self.variance = self.variance(self.sites,self.meanZmArea)
        if self.stratum.extrapolation == "area":
            self.a2js = self._site_attrs('a2j')
            self.Aij = sum(self.a2js)
            self.R = sum(self.zm_areas) / self.Aij
               
        # Soundwide Estimates
        self.zm_area = self.zm_area()
        self.zm_area_var = self.zm_area_var()
        self.se = self.se(self.zm_area_var)
        self.cv = self.cv(self.zm_area,self.se)

    #def __repr__(self):
        #return repr(self.sites)
        
    #def importSites(self,sites_list):
        #"""Create Site objects from a list of site data.
        
        #Append these sites objects to a sample
        
        #""" 
        #for s in sites_list:
            #args = s[:3]
            #if len(s) == 4:
                #a2j = s[3]
            #else:
                #a2j = None
            #kwargs = {'a2j':a2j,'conversion':self.conversion}
            #mySite = Site(*args,**kwargs)
            #self._addSite(mySite)
    
    #def _addSite(self,site):
        #""" Adds individual site objects to the sample. """
        #self.sites.append(site)

    #def set_stratum(self,stratum):
        #""" Sets the stratum object for the sample """
        #self.stratum = stratum
        
    #def _site_attrs(self,attr):
        #return [getattr(site,attr) for site in self.sites]

    #@property
    #def site_ids(self):
        #""" Fetch the list of the sample's site ids.
        
        #Note: the @property decorator allows for the 
        #method to behave like a 'read-only' attribute
        #so you can do something cleanly like:
        
        #>>> s = Sample()
        #>>> s.site_ids
        #[]
        
        #"""
        #return self._site_attrs('id')
        
    #def get_site_ids(self):
        #return self._site_attrs('id')
    
    #def get_zm_areas(self):
        #""" Fetch a list of the sample's site ZM areas """
        #return self._site_attrs('zmArea')

    #def get_zm_vars(self):
        #""" Fetch a list of the sample's site ZM area variances """
        #return self._site_attrs('zmAreaVar')
        
    def zm_area(self):
        """ Calculate Area of Zostera marina based on extrapolation type """
        #-- NO EXTRAPOLATION
        if self.stratum.extrapolation == "none":
            zmArea = sum(self.zm_areas)
        #-- AREA EXTRAPOLATION
        if self.stratum.extrapolation == "area":
            zmArea = sum(self.zm_areas) * self.stratum.A2 / self.Aij
        #-- LINEAR EXTRAPOLATION
        if self.stratum.extrapolation == "linear":
            zmArea = self.stratum.LT / self.stratum.LN * self.meanZmArea * self.stratum.Ni
        return zmArea
    
    def zm_area_var(self):
        """ Calculate Variance of Zostera marina Area based on extrapolation type """
        #-- NO EXTRAPOLATION
        if self.stratum.extrapolation == "none":
            zmAreaVar = sum(self.zm_vars)
        #-- AREA EXTRAPOLATION
        if self.stratum.extrapolation == "area":
            numerator1 = 0
            #print "site,zm_area_m2 (x2j), zm_var_m4, a2j, R, calc" 
            for x2j,a2j,id,var in zip(self.zm_areas,self.a2js,self.site_ids,self.zm_vars):
                # site_calc1 = ((x2j - (a2j * self.R)) ** 2) 
                site_calc = (x2j - a2j * float(self.R)) ** 2
                numerator1 = numerator1 + site_calc
                print "%s, %r, %r, %r, %r, %r" % (id, x2j, var, a2j, self.R, site_calc)
                
            #print "Final Numerator1: %r" % numerator1
            term1 = (self.stratum.Ni ** 2)
            term2 = 1 - (float(self.ni)/self.stratum.Ni)
            term3 = numerator1 / (float(self.ni) * (self.ni - 1))
            term4 = self.stratum.Ni * sum(self.zm_vars) / float(self.ni)
            #print "Sum of Variances %r" % (sum(self.zm_vars))
            #print "Term 1, Eq. 11: %r" % term1
            #print "Term 2, Eq. 11: %r" % term2
            #print "Term 3, Eq. 11: %r" % term3
            #print "Term 4, Eq. 11: %r" % term4
            #zmAreaVar = (self.stratum.Ni ** 2) * (1 - (self.ni/self.stratum.Ni)) * (numerator1 / (self.ni * (self.ni - 1)) ) + ((self.stratum.Ni * sum(self.zm_vars)) / self.ni)
            zmAreaVar = term1 * term2 * term3 + term4
        #-- LINEAR EXTRAPOLATION
        if self.stratum.extrapolation == "linear":
            #print "site,zm_area_m2 (x2j),zm_var_m4"            
            #for id,x2j,var in zip(self.site_ids,self.zm_areas,self.zm_vars):
            #    print id,x2j,var
            zmAreaVar = ( (self.stratum.LT / self.stratum.LN) ** 2 ) * (((self.stratum.Ni ** 2) * (1 - self.ni / self.stratum.Ni) * self.variance) / self.ni) + ((self.stratum.Ni / self.ni) * sum(self.zm_vars))
        return zmAreaVar
    
    def se(self,variance):
        """ Calculate the Standard Error """
        # Standard Error = Square Root of Variance
        return variance ** 0.5
    
    def cv(self,area,se):
        """ Calculate the coefficient of variation """
        # Coefficient of Variation = Standard Error / Zm Area
        return se / area

    #@property 
    #def ni(self):
        #""" The number of sites in the sample """
        #return len(self.sites)
        
    def meanZmArea(self,sites):
        """ Mean Z marina area for the Sample"""
        sumArea = 0
        for site in sites:
            sumArea = sumArea + site.zmArea
        meanArea = sumArea / float(len(sites))
        return meanArea
    
    def variance(self,sites,meanZmArea):
        """ Variance of Sample's Zm site areas """
        sum_sqdif = 0 # initialize sum of squared differences
        # Calculate sum of squared differences
        for site in sites:
            sqdif = (site.zmArea - meanZmArea) ** 2
            sum_sqdif = sqdif + sum_sqdif  
        # Standard Deviation
        stddev = ((1 / ( float(len(sites)) - 1 )) * sum_sqdif ) ** 0.5
        # Variance
        var = stddev ** 2
        return var
    
    #@property
    #def R(self):
        #""" Only for Rotational Flats """
        #return sum(self.zm_areas) / self.Aij
        

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