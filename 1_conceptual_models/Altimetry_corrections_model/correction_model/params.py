"""Module responsible for reading in IOP model and IOP LUT data."""

import configparser
import os
import pathlib
import logging
import numpy as np

def read_model_params(param_file="model_params.ini"):
    resolved_param_file=os.path.join(pathlib.Path(__file__).parent.resolve(), param_file)
    if not os.path.exists(resolved_param_file):
        print("IOP_model.ini file does not exist")
    __params = configparser.ConfigParser()
    __params.read(resolved_param_file)

    return __params
