"""Module responsible for reading in Rrs samples."""

import glob
import xarray as xr
import pathlib
import os

def read_reference_tracks(params):

    # read reference tracks
    track_names = params["tracks"]["reference_track_names"].split(',')
    resolved_path=os.path.join(pathlib.Path(__file__).parent.resolve(),
                               params["tracks"]["reference_track_dir"], 'ref??_*_??.nc')
    sample_files = glob.glob(resolved_path)
    reference_tracks = {}
    
    for sample_file, track_name in zip(sorted(sample_files), track_names):

        if "S3" in track_name:
            reference_tracks[track_name] = ["S3", xr.open_dataset(sample_file),
                                                  xr.open_dataset(sample_file)]
        elif "S6" in track_name:
            reference_tracks[track_name] = ["S6", xr.open_dataset(sample_file, group='data_01'),
                                                  xr.open_dataset(sample_file, group='data_01/ku')]
    return reference_tracks

def read_user_tracks(params):

    # read user tracks
    resolved_path=os.path.join(pathlib.Path(__file__).parent.resolve(),
                               params["tracks"]["user_track_dir"],'*.nc')
    sample_files = glob.glob(resolved_path)
    user_tracks = {}

    for sample_file in sample_files:

        file_name = os.path.basename(sample_file)
        if len(file_name) >= 40:
            file_name = file_name[0:40] + '...'
            
        if "S3" in sample_file:
            user_tracks[f"{file_name}"] = ["S3", xr.open_dataset(sample_file),
                                                 xr.open_dataset(sample_file)]
        elif "S6" in sample_file:
            user_tracks[f"{file_name}"] = ["S6", xr.open_dataset(sample_file, group='data_01'),
                                                 xr.open_dataset(sample_file, group='data_01/ku')]        
    return user_tracks