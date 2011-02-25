
#---------Functions--------------------------
# Function for inverting a dictionary
def invert_dict(dict):
    inverse = {}
    for (key, value) in dict.items():
        if value not in inverse:
            inverse[value] = []
        inverse[value].append(key)
    return inverse

# Get List of Site data, grouped by extrapolation type
def group_data_by_extrap(extrap_site_dict,extrap,site_stats_dict):
    # get the list of sites for the specified analysis stratum and extrapolation
    site_list = extrap_site_dict[extrap]
    
    # Extract the specified site data from the site statistics dictionary
    dat = []    
    for s in site_list:
        vals = site_stats_dict[s]
        dat.append(vals)
        
    return dat

#-------- Constants --------------
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

site_sampled_dict = {'site1':('frw','rotational'),  'site2':('fl','core'), 'site3':('fr','core'),'site4':('fl','persistent')} # this is dictionary 1
site_stats_dict = {'site1':('site1',34,5.0),  'site2':('site2',12,3.2), 'site3':('site3',19,3.3),'site4':('site4',25,4.3)} # this is dictionary 2

#--- Determine Analysis Stratum & Extrapolation Type (using geo and sampling strata lookup)
site_extrap = {}
for (siteid,data) in site_sampled_dict.items():
    site_extrap[siteid] = sw_Stratum4AreaCalcs[tuple(data)]

#--- Create a dictionary of extrapolation types that groups sites
extrap_site = invert_dict(site_extrap)


core_dat = group_data_by_extrap(extrap_site,core_extrap,site_stats_dict)
pfl_dat = group_data_by_extrap(extrap_site,pfl_extrap,site_stats_dict)
frw_dat = group_data_by_extrap(extrap_site,frw_extrap,site_stats_dict)

print core_dat
print pfl_dat
print frw_dat