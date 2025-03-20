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
        self.track_name = self.conditions["track_names"][0]
        
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
        selection_radio_widget, self.correction_check_box_widgets, self.corrections,\
          self.flag_check_box_widgets, self.flags, self.flag_values, reference_surface_radio_widget, self.range_slider,\
          clear_corr_button, clear_flag_button = build_widgets(self)

        # set layouts for plots and control panels
        col1w = "300px"
        row1h = "185px"
        col2w = "350px"
        row2h = "550px"
        col3w = "100px"
        
        # set control panel for corrections
        self.controls_corr = widgets.VBox([
            self.correction_check_box_widgets[f"corr_{str(ii).zfill(2)}"] for ii in range(len(self.corrections))])
        self.controls_corr.layout = make_box_layout(width="270px", height="450px", border=None)

        # set control panel for flags
        self.controls_flags1 = widgets.VBox([
            self.flag_check_box_widgets[f"flag_{str(ii).zfill(2)}"] for ii in range(0,3)])

        self.controls_flags2 = widgets.VBox([
            self.flag_check_box_widgets[f"flag_{str(ii).zfill(2)}"] for ii in range(3,6)])
        
        self.controls_flags3 = widgets.VBox([
            self.flag_check_box_widgets[f"flag_{str(ii).zfill(2)}"] for ii in range(6,10)])
    
        # top row components
        self.output_spatial_plot.layout = make_box_layout(width=col1w, height=row1h, border=None)
        selection_radio_widget.layout = make_box_layout(width=col2w, height="185px")
        reference_surface_radio_widget.layout = make_box_layout(width=col2w, height="185px")
        self.first_row = widgets.HBox([self.output_spatial_plot, selection_radio_widget, reference_surface_radio_widget])

        # second row components
        self.controls_corr_full = widgets.VBox([widgets.HTML(description="𝗖𝗼𝗿𝗿𝗲𝗰𝘁𝗶𝗼𝗻𝘀:", value="",), self.controls_corr, clear_corr_button])
        self.controls_corr_full.layout = make_box_layout(width=col1w, height=row2h)        
        self.range_slider.layout = make_box_layout(width=col3w)
        self.output_corr_plot.layout = make_box_layout(width="600px")
        self.second_row = widgets.HBox([self.controls_corr_full, self.output_corr_plot, self.range_slider]) 

        # third row components
        
        self.controls_flags_full0 = widgets.VBox([widgets.HTML(description="𝗙𝗹𝗮𝗴𝘀:", value="",), clear_flag_button])
        self.controls_flags_full1 = widgets.VBox([self.controls_flags1])
        self.controls_flags_full2 = widgets.VBox([self.controls_flags2])
        self.controls_flags_full3 = widgets.VBox([self.controls_flags3])
        self.third_row = widgets.HBox([self.controls_flags_full0, self.controls_flags_full1,
                                       self.controls_flags_full2, self.controls_flags_full3])
        self.third_row.layout = make_box_layout(width="1020px", height="135px")

        # add to children
        self.children = [self.first_row, self.second_row, self.third_row]
                
        # ---TRIGGERS---
        # changes to track selection
        selection_radio_widget.observe(self.change_track, 'value')

        # changes to reference surface
        reference_surface_radio_widget.observe(self.change_reference_surface, 'value')

        # changes to range slider
        self.range_slider.observe(self.update_view, 'value')
        
        # changes to corrections
        for ii in range(len(self.corrections)): 
            self.correction_check_box_widgets[f"corr_{str(ii).zfill(2)}"].observe(self.change_corrections_flags, 'value')
        
        # changes to flags
        for ii in range(len(self.flags)): 
            self.flag_check_box_widgets[f"flag_{str(ii).zfill(2)}"].observe(self.change_corrections_flags, 'value')
        
        # clear corrections
        clear_corr_button.on_click(self.on_corr_button_clicked)
        
        # clear flags
        clear_flag_button.on_click(self.on_flag_button_clicked)
        
        # show track min/max
        
    # range slider control
    def update_view(self, change):
        """refine plot extents"""
        
        low_lat_val = self.children[1].children[2].value[0]
        high_lat_val = self.children[1].children[2].value[1]

        # change spatial map
        ii = np.where((self.vars["lat"] >= low_lat_val) & (self.vars["lat"] <= high_lat_val))[0]
        low_lon_val = self.vars["lon"][ii[0]]
        high_lon_val = self.vars["lon"][ii[-1]]    

        if (low_lat_val == -90.0) and (high_lat_val == 90.0):
            self.ax_spatial.set_global()
            self.ax_spatial.set_aspect(1.5)
        else:
            self.ax_spatial.set_extent([low_lon_val, high_lon_val, low_lat_val, high_lat_val])
            self.ax_spatial.set_aspect(np.abs(high_lon_val - low_lon_val) / (high_lat_val - low_lat_val)/2*1.5)

        try:
            datamax = max([np.nanmax(self.vars["data_ref"][ii]), np.nanmax(self.vars["data_corr"][ii])])
            datamin = min([np.nanmin(self.vars["data_ref"][ii]), np.nanmin(self.vars["data_corr"][ii])])
        except:
            datamax = np.nanmax(self.vars["data_ref"][ii])
            datamin = np.nanmin(self.vars["data_ref"][ii])
            
        # change correction map
        self.ax_corr.set_xlim([datamin - (datamax-datamin)/10, datamax + (datamax-datamin)/10])
        self.ax_corr.set_ylim([low_lat_val, high_lat_val])

    # track selection radio button control
    def change_track(self, change):
        self.track_name = self.children[0].children[1].value

        if change.new:
            # update data
            calculate_variables(self)
            select_reference_surface(self)
            make_trace = recalculate_corrections_flags(self)

            # plot limit calculations
            datamax = np.nanmax(self.vars["data_ref"])
            datamin = np.nanmin(self.vars["data_ref"])

            # reset corr view....
            self.ax_corr.line1a.set_offsets([[i,j] for i,j in zip(self.vars["data_ref"], self.vars["lat"])])
            self.ax_corr.set_xlim([datamin - (datamax-datamin)/10, datamax + (datamax-datamin)/10])
            
            # reset spatial view
            self.ax_spatial.line2a.remove()
            self.ax_spatial.line2a = self.ax_spatial.scatter(self.vars["lon"], self.vars["lat"],
                                                             c=self.vars["data_ref"],
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
        
        self.reference_surface = self.children[0].children[2].value
        
        if change.new:
            select_reference_surface(self)
            make_trace = recalculate_corrections_flags(self)
            
            # plot limit calculations
            datamax = np.nanmax(self.vars["data_ref"])
            datamin = np.nanmin(self.vars["data_ref"])
  
            # update corr view
            self.ax_corr.line1a.set_offsets([[i,j] for i,j in zip(self.vars["data_ref"], self.vars["lat"])])
            
            self.ax_corr.set_xlim([datamin - (datamax-datamin)/10, datamax + (datamax-datamin)/10])
            self.ax_corr.plot_legend.get_texts()[0].set_text(self.varname)
            self.ax_corr.set_xlabel(self.varname)

            # update spatial view
            self.ax_spatial.line2a.remove()
            self.ax_spatial.line2a = self.ax_spatial.scatter(self.vars["lon"], self.vars["lat"],
                                                             c=self.vars["data_ref"],
                                                             cmap=plt.cm.RdYlBu_r,
                                                             s=20, marker='o', edgecolors=None,
                                                             linewidth=0.0, zorder=3)
            # recalculate corrections
            replot_corrections(self, make_trace)
            
            self.update_view(change)

    # correction check box controls
    def change_corrections_flags(self, change):

        make_trace = recalculate_corrections_flags(self)
        replot_corrections(self, make_trace)

        # update spatial view
        self.ax_spatial.line2a.remove()
        self.ax_spatial.line2a = self.ax_spatial.scatter(self.vars["lon"], self.vars["lat"],
                                                         c=self.vars["data_ref"],
                                                         cmap=plt.cm.RdYlBu_r,
                                                         s=20, marker='o', edgecolors=None,
                                                         linewidth=0.0, zorder=3)
        self.update_view(change)

    def on_corr_button_clicked(self, b):
        self.clear_corrections()
    
    def clear_corrections(self):
        for ii in range(len(self.corrections)): 
            self.correction_check_box_widgets[f"corr_{str(ii).zfill(2)}"].value = False

    def on_flag_button_clicked(self, b):
        self.clear_flags()
    
    def clear_flags(self):
        for ii in range(len(self.flags)): 
            self.flag_check_box_widgets[f"flag_{str(ii).zfill(2)}"].value = False