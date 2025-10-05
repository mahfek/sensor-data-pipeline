import pandas as pd
from netCDF4 import Dataset

from .base_file import BaseFile


class NetCDFFile(BaseFile):
    # target variables from NetCDF file
    target_vars = ["azimuth", "elevation","time", "range",'cnr','radial_wind_speed']

    def read(self) -> dict:
        # define output format
        data = {k: [] for k in self.target_vars}

        # open a NetCDF file
        ds = Dataset(self.path, mode="r")

        # Iterate over all groups in the NetCDF file
        for g_name in ds.groups:
            group = ds.groups[g_name]
            # Iterate over variables in the group
            for var_name in group.variables:
                if var_name in self.target_vars:
                   var_data = group.variables[var_name]
                   data[var_name] = var_data[:].tolist()

        return data