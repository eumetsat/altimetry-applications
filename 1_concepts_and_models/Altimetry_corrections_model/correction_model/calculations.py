"""Module responsible for the numerical calculations of the model."""

import numpy as np

def calculate_variables(self):
    # reads in the necessary variables from the data and calculates some fundamental values
    
    self.vars = {}
    # direct variables: Sentinel-3 1 Hz (could add selectables for 20 Hz (but don't really see the point)
    S3_SRAL = True
    
    if "S3_SRAL":
        variables = {"alt" : "alt_01",
                     "range" : "range_ocean_01_ku",
                     "mdt" : "mean_dyn_topo_01",
                     "geoid" : "geoid_01",
                     "lat" : "lat_01",
                     "lon" : "lon_01",
                     "ssha" : "ssha_01_ku",
                     "iono" : "iono_cor_alt_01_ku",
                     "dry" : "mod_dry_tropo_cor_meas_altitude_01",
                     "wet" : "rad_wet_tropo_cor_01_ku",
                     "ocean" : "ocean_tide_sol1_01",
                     "no_eq" : "ocean_tide_non_eq_01",
                     "internal" : "internal_tide_sol1_01",
                     "solid" : "solid_earth_tide_01",
                     "pole" : "pole_tide_01",
                     "hf" : "hf_fluct_cor_01",
                     "ss_bias" : "sea_state_bias_01_ku",
                     "surf_class" : "surf_class_01",
                     "surf_type" : "surf_type_01"}
    else:
        # WIP: need to factor in the damn annoying change to netCDF group structure!
        print("Sentinel-6 not yet implemented")
    
    for key in variables:
        if "lon" in key or "lat" in key:
            self.vars[key] = self.all_tracks[self.track_number][variables[key]].data
        else:
            self.vars[key] = self.all_tracks[self.track_number][variables[key]]
    
    for key in variables:
        # apply flag generically, removing everything that is not ocean
        # WIP: could add a tick box to make this selectable
        if not "lon" in key and not "lat" in key and not "surf_type" in key and not "surf_class" in key:
            self.vars[key][self.vars["surf_class"] != 0] = np.nan 
        
    # calculated variables
    self.vars["mss_raw"] = self.vars["geoid"] + self.vars["mdt"]
    self.vars["ssh_raw"] = self.vars["alt"] - self.vars["range"]
    self.vars["ssha_raw"] = self.vars["ssh_raw"] - self.vars["mss_raw"]
    self.vars["adt_raw"] = self.vars["ssha_raw"] + self.vars["mdt"]

def box_switch(self, box_range, disabled_state=True):
    for ii in box_range:
        self.controls_corr.children[ii].disabled = disabled_state

def select_reference_surface(self):
    # selects the reference surface
    
    if self.reference_surfaces[0] in self.reference_surface: 
        self.vars["data_raw"] = self.vars["ssh_raw"]
        self.varname = "SSH [m] (raw)"
        
    elif self.reference_surfaces[1] in self.reference_surface:
        self.vars["data_raw"] = self.vars["ssha_raw"]
        self.varname = "SSHA [m] (raw)"
    
    elif self.reference_surfaces[2] in self.reference_surface:
        self.vars["data_raw"] = self.vars["adt_raw"]
        self.varname = "ADT [m] (raw)"

def recalculate_corrections(self):
    # (re-)calculates the corrections
    
    # count the logic
    tick_logic = []
    for ii in range(0, len(self.children[1].children[0].children[1].children)):
        tick_logic.append(self.children[1].children[0].children[1].children[ii].value)

    if sum(tick_logic) == 0:
        self.vars["data_corr"] = None
        make_trace = False
    else:
        self.vars["data_corr"] = self.vars["data_raw"]
        make_trace = True

    # work through the logic for the check-boxes
    if tick_logic[0]:
        self.vars["data_corr"] = self.vars["data_corr"] - self.vars["iono"] - self.vars["dry"] \
                                 - self.vars["wet"] - self.vars["ocean"] - self.vars["no_eq"] \
                                 - self.vars["internal"] - self.vars["solid"] - self.vars["pole"] \
                                 - self.vars["hf"] - self.vars["ss_bias"]
        box_switch(self, range(1, 13), disabled_state=True)
    else:
        box_switch(self, range(1, 13), disabled_state=False)

    if tick_logic[1] and not tick_logic[0]:
        self.vars["data_corr"] = self.vars["data_corr"] - self.vars["iono"]

    if tick_logic[2] and not tick_logic[0]:
        self.vars["data_corr"] = self.vars["data_corr"] - self.vars["dry"]

    if tick_logic[3] and not tick_logic[0]:
        self.vars["data_corr"] = self.vars["data_corr"] - self.vars["wet"]

    if tick_logic[4] and not tick_logic[0]:
        self.vars["data_corr"] = self.vars["data_corr"] - self.vars["ocean"] - self.vars["no_eq"] \
                                 - self.vars["internal"] - self.vars["solid"] - self.vars["pole"]
        box_switch(self, range(5, 11), disabled_state=True)
    elif not tick_logic[4] and not tick_logic[0]:
        box_switch(self, range(5, 11), disabled_state=False)
        
    if tick_logic[5] and not tick_logic[4] and not tick_logic[0]:
        self.vars["data_corr"] = self.vars["data_corr"] - self.vars["ocean"] - self.vars["no_eq"] \
                                 - self.vars["internal"]
        box_switch(self, range(6, 9), disabled_state=True)
    elif not tick_logic[5] and not tick_logic[4] and not tick_logic[0]:
        box_switch(self, range(6, 9), disabled_state=False)

    if tick_logic[6] and not tick_logic[5] and not tick_logic[4] and not tick_logic[0]:
        self.vars["data_corr"] = self.vars["data_corr"] - self.vars["ocean"]

    if tick_logic[7] and not tick_logic[5] and not tick_logic[4] and not tick_logic[0]:
        self.vars["data_corr"] = self.vars["data_corr"] - self.vars["no_eq"]

    if tick_logic[8] and not tick_logic[5] and not tick_logic[4] and not tick_logic[0]:
        self.vars["data_corr"] = self.vars["data_corr"] - self.vars["internal"]

    if tick_logic[9] and not tick_logic[4] and not tick_logic[0]:
        self.vars["data_corr"] = self.vars["data_corr"] - self.vars["solid"]

    if tick_logic[10] and not tick_logic[4] and not tick_logic[0]:
        self.vars["data_corr"] = self.vars["data_corr"] - self.vars["pole"]

    if tick_logic[11] and not tick_logic[0]:
        self.vars["data_corr"] = self.vars["data_corr"] - self.vars["hf"]

    if tick_logic[12] and not tick_logic[0]:
        self.vars["data_corr"] = self.vars["data_corr"] - self.vars["ss_bias"]

    return make_trace