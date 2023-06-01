"""Module responsible for building the Jupyter notebook widgets for model interaction."""
from ipywidgets import widgets, Layout
import os

def build_widgets(self, width="250px"):

    # define track selection radio widget
    selection_radio_widget = widgets.RadioButtons(
        options=self.conditions["track_names"],
        description='Track:',
        layout=widgets.Layout(width=width),
        disabled=False)

    # define correction widget check boxes
    correction_check_box_widgets = {}
    
    corrections = ["All ocean geophysical",
                   "Ionosphere",
                   "Dry troposphere",
                   "Wet troposphere",
                   "All tides",
                   "All ocean tides",
                   "Ocean tide",
                   "Ocean tide non-equilibrium",
                   "Internal ocean tide",
                   "Solid earth tide",
                   "Pole tide",
                   "High frequency fluctuations/IB",
                   "Sea State Bias"]

    count = 0
    for correction in corrections:
        correction_check_box_widgets[f"corr_{str(count).zfill(2)}"] = widgets.Checkbox(
        value=False,
        description=correction,
        disabled=False,
        indent=False,
        layout=Layout(width=width))
        count = count + 1

    # define reference selection widgets
    reference_surface_radio_widget = widgets.RadioButtons(
        options=self.reference_surfaces,
        description='Reference surface:',
        layout=Layout(width=width),
        disabled=False)

    # define lat selector widget
    range_slider = widgets.FloatRangeSlider(value=[-90, 90],
                                            min=-90.0,
                                            max=90.0,
                                            step=0.1,
                                            description='Latitude:')
    
    return selection_radio_widget, correction_check_box_widgets, corrections, reference_surface_radio_widget, range_slider