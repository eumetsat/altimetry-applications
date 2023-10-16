"""Module responsible for the core logic of the forward model."""

import ipywidgets as widgets
import matplotlib.pyplot as plt
import numpy as np
import os
import functools

from correction_model.params import read_model_params
from correction_model.samples import *
from correction_model.plots import *
from correction_model.widgets import build_widgets
from correction_model.calculations import *

def make_box_layout(width="auto", height="auto", margin='0px 10px 10px 0px', border='solid 1px black'):
     return widgets.Layout(
        border=border,
        margin=margin,
        padding='5px 5px 5px 5px',
        width=width,
        height=height
     )

class CorrectionModel(widgets.VBox):
     
    def __init__(self):
        # initialise the super class
        super().__init__()

        # read parameter values
        self.conditions = {}
        self.conditions["params"] = read_model_params()

        # read tracks
        reference_tracks = read_reference_tracks(self.conditions["params"])
        users_tracks = read_user_tracks(self.conditions["params"])
        self.all_tracks = reference_tracks | users_tracks
        self.conditions["track_names"] = list(self.all_tracks.keys())

        # set default track
        self.track_number = self.conditions["track_names"][0]

        # set default reference surface
        self.reference_surfaces = ["Reference ellipsoid", "Mean Sea Surface (geoid+MDT)", "Geoid"]
        self.reference_surface = self.reference_surfaces[0]
        
        # setup output streams for plots
        self.output_corr_plot = widgets.Output()
        self.output_spatial_plot = widgets.Output()

        # define parameters for "spectral" plots
        set_corr_plot(self)
        set_spatial_plot(self)
        
        # define widgets
        selection_radio_widget, correction_check_box_widgets, corrections, \
            reference_surface_radio_widget, self.range_slider = build_widgets(self)

        # set control panel for corrections
        self.controls_corr = widgets.VBox([
            correction_check_box_widgets["corr_00"],
            correction_check_box_widgets["corr_01"],
            correction_check_box_widgets["corr_02"],
            correction_check_box_widgets["corr_03"],
            correction_check_box_widgets["corr_04"],
            correction_check_box_widgets["corr_05"],
            correction_check_box_widgets["corr_06"],
            correction_check_box_widgets["corr_07"],
            correction_check_box_widgets["corr_08"],
            correction_check_box_widgets["corr_09"],
            correction_check_box_widgets["corr_10"],
            correction_check_box_widgets["corr_11"],
            correction_check_box_widgets["corr_12"]
        ])

        # set layouts for plots and control panels
        width_left = "275px"
        width_right = "770px"
        
        # top row components
        self.output_spatial_plot.layout = make_box_layout(width=width_left, height="150px", border=None)
        selection_radio_widget.layout = make_box_layout(width=width_right)
        self.range_slider.layout = make_box_layout(width=width_right)
        self.selectors = widgets.VBox([selection_radio_widget, self.range_slider])
        self.first_row = widgets.HBox([self.output_spatial_plot, self.selectors]) 

        # second row components
        reference_surface_radio_widget.layout = make_box_layout(width=width_left)
        self.controls_corr.layout = make_box_layout(width=width_left)        
        self.controls = widgets.VBox([reference_surface_radio_widget, self.controls_corr])
        self.output_corr_plot.layout = make_box_layout()
        self.second_row = widgets.HBox([self.controls, self.output_corr_plot]) 

        # add to children
        self.children = [self.first_row, self.second_row]

        # ---TRIGGERS---
        # changes to track selection
        selection_radio_widget.observe(self.change_track, 'value')

        # changes to reference surface
        reference_surface_radio_widget.observe(self.change_reference_surface, 'value')

        # changes to range slider
        self.range_slider.observe(self.update_model, 'value')
        
        # changes to corrections
        correction_check_box_widgets["corr_00"].observe(self.change_correction, 'value')  #special - implement all except 4/5
        correction_check_box_widgets["corr_01"].observe(self.change_correction, 'value')
        correction_check_box_widgets["corr_02"].observe(self.change_correction, 'value')
        correction_check_box_widgets["corr_03"].observe(self.change_correction, 'value')
        correction_check_box_widgets["corr_04"].observe(self.change_correction, 'value')  #special - implement all tides
        correction_check_box_widgets["corr_05"].observe(self.change_correction, 'value')  #special - implement all ocean tides
        correction_check_box_widgets["corr_06"].observe(self.change_correction, 'value')
        correction_check_box_widgets["corr_07"].observe(self.change_correction, 'value')
        correction_check_box_widgets["corr_08"].observe(self.change_correction, 'value')
        correction_check_box_widgets["corr_09"].observe(self.change_correction, 'value')
        correction_check_box_widgets["corr_10"].observe(self.change_correction, 'value')
        correction_check_box_widgets["corr_11"].observe(self.change_correction, 'value')
        correction_check_box_widgets["corr_12"].observe(self.change_correction, 'value')
        
        # show track min/max
        
    # range slider control
    def update_model(self, change):
        """refine plot extents"""
        
        low_lat_val = self.children[0].children[1].children[1].value[0]
        high_lat_val = self.children[0].children[1].children[1].value[1]

        # change spatial map
        ii = np.where((self.vars["lat"] >= low_lat_val) & (self.vars["lat"] <= high_lat_val))[0]
        low_lon_val = self.vars["lon"][ii[0]]
        high_lon_val = self.vars["lon"][ii[-1]]    

        if (low_lat_val == -90.0) and (high_lat_val == 90.0):
            self.ax_spatial.set_global()
            self.ax_spatial.set_aspect(2)
        else:
            self.ax_spatial.set_extent([low_lon_val, high_lon_val, low_lat_val, high_lat_val])
            self.ax_spatial.set_aspect(np.abs(high_lon_val - low_lon_val) / (high_lat_val - low_lat_val))

        # change correction map
        self.ax_corr.set_ylim([low_lat_val, high_lat_val])

    # track selection radio button control
    def change_track(self, change):
        
        self.track_number = self.children[0].children[1].children[0].value

        if change.new:
            # update data
            calculate_variables(self)
            select_reference_surface(self)
            make_trace = recalculate_corrections(self)

            # plot limit calculations
            datamax = np.nanmax(self.vars["data_raw"])
            datamin = np.nanmin(self.vars["data_raw"])

            # reset corr view....
            self.ax_corr.line1a.set_xdata(self.vars["data_raw"])
            self.ax_corr.line1a.set_ydata(self.vars["lat"])
            self.ax_corr.set_xlim([datamin - (datamax-datamin)/10, datamax + (datamax-datamin)/10])
            
            # reset spatial view
            self.ax_spatial.line2a.remove()
            self.ax_spatial.line2a = self.ax_spatial.scatter(self.vars["lon"], self.vars["lat"],
                                                             c=self.vars["data_raw"],
                                                             cmap=plt.cm.RdYlBu_r,
                                                             s=20, marker='o', edgecolors=None,
                                                             linewidth=0.0, zorder=3)

            # recalculate corrections
            replot_corrections(self, make_trace)

            # reset slider and views
            self.range_slider.value = [-90.0, 90.0]            
            self.ax_corr.set_ylim([-90, 90])
            self.ax_spatial.set_global()

    # reference surface selection radio button control
    def change_reference_surface(self, change):
        
        self.reference_surface = self.children[1].children[0].children[0].value
        
        if change.new:
            select_reference_surface(self)
            make_trace = recalculate_corrections(self)
            
            # plot limit calculations
            datamax = np.nanmax(self.vars["data_raw"])
            datamin = np.nanmin(self.vars["data_raw"])
  
            # update corr view....
            self.ax_corr.line1a.set_xdata(self.vars["data_raw"])
            self.ax_corr.line1a.set_ydata(self.vars["lat"])
            self.ax_corr.set_xlim([datamin - (datamax-datamin)/10, datamax + (datamax-datamin)/10])
            self.ax_corr.plot_legend.get_texts()[0].set_text(self.varname)
            self.ax_corr.set_xlabel(self.varname)

            # recalculate corrections
            replot_corrections(self, make_trace)

    # correction check box controls
    def change_correction(self, change):

        make_trace = recalculate_corrections(self)
        replot_corrections(self, make_trace)
