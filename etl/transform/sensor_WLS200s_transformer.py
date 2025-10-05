import pandas as pd
from datetime import datetime
import math

from .base_transformer import BaseTransformer

class SensorWLS200sTransformer(BaseTransformer):
    ELEVATION_TARGET = 89  

    def run_transformations(self):
        #find max elevation index
        index = self.get_index_of_max_elevation(list(self.data.get('elevation', [])))
        self.data["elevation_index "] = index

        # convert timestamp 
        formatted_times = self.convert_time_to_datetime_str(list(self.data.get('time', [])))

    
        return self.data


    #Convert list of timestamps into formatted datetime strings.
    def convert_time_to_datetime_str(self,time_list):
        formatted = [datetime.fromtimestamp(item).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                 for item in time_list]
        
        self.data['time'] = formatted
        return formatted
    
    #Find max elevation where integer part equals ELEVATION_TARGET.
    def get_index_of_max_elevation(self,elevation_list):
        candidates = [float(item )for item in elevation_list 
                      if math.modf(float(item)) [1] == self.ELEVATION_TARGET]
        
        if candidates:
            max_value = max(candidates)
            try:
                return elevation_list.index(max_value)
            except ValueError:
                return None
        return None
