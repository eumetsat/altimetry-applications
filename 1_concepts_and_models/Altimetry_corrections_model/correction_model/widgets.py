"""Module responsible for building the Jupyter notebook widgets for model interaction."""
from ipywidgets import widgets, Layout
import os

def build_widgets(self, width="250px"):

    # define track selection radio widget
    selection_radio_widget = widgets.RadioButtons(
        options=self.conditions["track_names"],
        description='𝗧𝗿𝗮𝗰𝗸:',
        layout=widgets.Layout(width=width),
        disabled=False)

    # define correction widgets: check boxes
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

    # define correction widgets: clear all corrections
    clear_corr_button = widgets.Button(
                                    description='Clear corrections',
                                    disabled=False,
                                    button_style='info',
                                    tooltip='Button to clear all active corrections',
                                    icon='check' # (FontAwesome names without the `fa-` prefix)
                                   )

    # define flag widgets: check boxes
    flag_check_box_widgets = {}
    
    flags = ["Surface class (open ocean)",
             "Surface class (land)",
             "Surface class (continental water)",
             "Surface class (aquatic vegetation)",
             "Surface class (continental ice/snow)",
             "Surface class (floating ice)",
             "Surface class (salted basin)",
             "Surface type (ocean_or_semi_enclosed_sea)",
             "Surface type (enclosed_sea_or_lake)",
             "Surface type (continental_ice)",
             "Surface type (land)"]
    
    flag_values = [0,1,2,3,4,5,6,0,1,2,3]
    
    count = 0
    for flag in flags:
        if "ocean" in flag:
            set_val = False
            set_disabled = True
        else:
            set_val = True
            set_disabled = False
        flag_check_box_widgets[f"flag_{str(count).zfill(2)}"] = widgets.Checkbox(
        value=set_val,
        description=flag,
        disabled=set_disabled,
        indent=False,
        layout=Layout(width=width))
        count = count + 1

    # clear all flags button
    clear_flag_button = widgets.Button(
                                    description='Clear flags',
                                    disabled=False,
                                    button_style='info',
                                    tooltip='Button to clear all active flags',
                                    icon='check' # (FontAwesome names without the `fa-` prefix)
                                   )

    # define reference surface selection widgets
    reference_surface_radio_widget = widgets.RadioButtons(
        options=self.reference_surfaces,
        description='𝗥𝗲𝗳𝗲𝗿𝗲𝗻𝗰𝗲 𝘀𝘂𝗿𝗳𝗮𝗰𝗲:',
        layout=Layout(width=width),
        disabled=False)

    # define latitude selector widget
    range_slider = widgets.FloatRangeSlider(value=[-90, 90],
                                            min=-90.0,
                                            max=90.0,
                                            step=0.1,
                                            orientation='vertical',
                                            description='Latitude:')
    
    return selection_radio_widget, correction_check_box_widgets, corrections, flag_check_box_widgets, flags, \
           flag_values, reference_surface_radio_widget, range_slider, clear_corr_button, clear_flag_button