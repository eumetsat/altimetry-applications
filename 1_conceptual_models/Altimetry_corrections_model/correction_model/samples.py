"""Module responsible for reading in Rrs samples."""

import glob
import xarray as xr
import pathlib
import os

def read_reference_tracks(params):

    # read reference tracks
    track_names = params["tracks"]["reference_track_names"].split(',')
    resolved_path=os.path.join(pathlib.Path(__file__).parent.resolve(), params["tracks"]["reference_track_dir"],'*standard*.nc')
    sample_files = glob.glob(resolved_path)
    reference_tracks = {}
    for sample_file, track_name in zip(sorted(sample_files), track_names):
        reference_tracks[track_name] = xr.open_dataset(sample_file)

    return reference_tracks

def read_user_tracks(params):

    # read user tracks
    resolved_path=os.path.join(pathlib.Path(__file__).parent.resolve(), params["tracks"]["user_track_dir"],'*standard*.nc')
    sample_files = glob.glob(resolved_path)
    user_tracks = {}
    count = 0
    for sample_file in sample_files: 
        user_tracks[f"User_{str(count).zfill(2)}"] = xr.open_dataset(sample_file)
        count = count + 1
        
    return user_tracks