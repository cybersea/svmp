""" Spatial Classes for SVMP Tools Module """

import arcgisscripting

class TableQuery(object):
    """ Represents a non-spatial query on an ArcGIS table
    
    A TableQuery requires a geoprocessing object, table, and
    an optional query string

        Attributes:
    gp -- an ArcGIS geoprocessing object
    tbl -- full path to an ArcGIS table
    query -- [optional] an ArcGIS query string (the "where" clause)
    fields -- list of fields in feature class

    """
    
    def __init__(self,gp,tbl,query=""):
        self.gp = gp
        self.tbl = tbl
        self.query = query 
        self.fields = self.get_field_list()
        
    def __repr__(self):
        return repr((self.gp,self.tbl,self.query))
    
    def get_field_list(self):
        """ Fetch a list of the fields in the table """
        fields = self.gp.Describe(self.tbl).Fields
        field_list = []
        fld = fields.Next()
        # print fld
        while fld:
            field_list.append(fld.Name)
            fld = fields.Next()
        return field_list
    
    @property
    def record_count(self):
        """ Counts the number of queried records
        or all records if no query is provided """
        rec_count = 0 # initialize count
        records = self.gp.SearchCursor(self.tbl,self.query)
        record = records.Next()
        while record:
            rec_count = rec_count + 1
            record = records.Next()         
        del record, records
        return rec_count
    
    def field_results(self,field_list,unique=None):
        """ Gets the query results from the specified fields
        Stores each row as a list
        The results are a dictionary with an optional field name as
        the key, or a default automatically-generated numeric key
        """
        #print self.query
        #fields = args  # any number of field names
        results = {}  # initialize dictionary for all results       
        records = self.gp.SearchCursor(self.tbl,self.query)
        record = records.Next()
        row_id = 1 # initialize counter for use if no unique field provided for dictionary key
        # Loop through all records in cursor
        while record:
            if unique:
                row_id = record.getValue(unique)
            else:
                row_id = row_id + 1
            # loop through all fields in list
            row_data = [] #{} # initialize list for each row's results
            # Query each field for that row and add values to a list
            for fld in field_list:
                # Raise error if a field does not exist in the feature class
                if fld not in self.fields:
                    raise ValueError("The field, %s, does not exist in feature class, %s" % (fld,self.fc))
                # All non-geometry fields
                else:
                    #row_data[fld] = record.getValue(fld)
                    val = record.getValue(fld)
                row_data.append(val)
            # Add row results to complete query results list
            #results.append(row_data)
            results[str(row_id)] = row_data
            record = records.Next()

        del record, records
        return results

#class FeatureQuery(object):
class FeatureQuery(TableQuery):

    """ Represents a query on an ArcGIS spatial feature class 
    Subclass of TableQuery
    
    A FeatureQuery requires a geoprocessing object, feature class, 
    an optional query string
    
    Attributes:
    gp -- an ArcGIS geoprocessing object
    fc -- full path to an ArcGIS feature class
    query -- [optional] an ArcGIS query string (the "where" clause)
    geom_type -- Feature class's geometry type
    shape_field -- Shape field name
    
    """
    
    def __init__(self,gp,fc,query=""):
        TableQuery.__init__(self,gp,fc,query="")
        self.fc = self.tbl   # is this the right way to do this?
        #  A feature class is just a special kind of table....
        self.geom_type = self.get_geom_type()
        self.shape_field = self.get_shape_field()
        
    #def __repr__(self):
        #return repr((self.gp,self.fc,self.query))
    
    def get_geom_type(self):
        """ Fetches the geometry type of the feature class """
        return self.gp.Describe(self.fc).ShapeType
    
    def get_shape_field(self):
        return self.gp.Describe(self.fc).ShapeFieldName
        
    def get_linear_units(self): 
        """ Fetches the linear units of the feature class """
        prjType = self.gp.Describe(self.fc).SpatialReference.Type
        if prjType == "Projected":
            return self.gp.Describe(self.fc).SpatialReference.LinearUnitName
        elif prjType == "Geographic":
            return "Degrees"
        else:
            return "unknown units"
       
    @property
    def geometry_sum(self):
        """ Sums the values for the geometry (Area or Length)"""
        geom_sum = 0 # initialize sum
        # Create a Search Cursor with the feature class and query text
        records = self.gp.SearchCursor(self.fc,self.query)
        record = records.Next()
        # loop through all records and sum the geometry value
        while record:
            geom_sum = geom_sum + self._geometry_size(record)
            record = records.Next()
        del record,records  # get rid of cursors      
        return geom_sum
    
    # This is essentially a repeat of the field_results in the Super Class
    #   but, with added handling of the geometry field here.
    #   Let me know if there is a better way to do this.
    def field_results(self,field_list,unique=None):
        """ Gets the query results from the specified fields 
        Stores each row as a list
        The results are a dictionary with an optional field name as
        the key, or a default automatically-generated numeric key
        """
        #fields = #args  # any number of field names
        results = {} #[]  # initialize list for all results       
        records = self.gp.SearchCursor(self.fc,self.query)
        record = records.Next()
        row_id = 1 # initialize counter for use if no unique field provided for dictionary key
        # Loop through all records in cursor
        while record:
            if unique:
                row_id = record.getValue(unique)
            else:
                row_id = row_id + 1
            # loop through all fields in list
            row_data = [] #{} # initialize list for each row's results
            # Query each field for that row and add values to a list
            for fld in field_list:
                # Raise error if a field does not exist in the feature class
                if fld not in self.fields:
                    raise ValueError("The field, %s, does not exist in feature class, %s" % (fld,self.fc))
                # Geometry field query
                if fld == self.shape_field:
                    # row_data[fld] = self._geometry_size(record)
                    val = self._geometry_size(record)
                # All other non-geometry fields
                else:
                    #row_data[fld] = record.getValue(fld)
                    val = record.getValue(fld)
                row_data.append(val)
            # Add row results to complete query results list
            #results.append(row_data)
            results[str(row_id)] = row_data
            record = records.Next()
        del record, records
        return results
    
    def _geometry_size(self,record):
        """ Gets a size value from the current record in the geometry field for 
        polygon (Area) or
        polyline (Length)      
        """
        if self.geom_type == "Polygon":
            # AREA
            return record.getValue(self.shape_field).Area
        elif self.geom_type == "Polyline":
            # LENGTH
            return record.getValue(self.shape_field).Length
        else:
            raise ValueError('Shape Type, %s, must be Polygon or Polyline to query its size' % self.geom_type)
        
        
        