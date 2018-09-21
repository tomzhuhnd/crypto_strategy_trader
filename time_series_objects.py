# Import generic libraries
import datetime

class time_series_vol_weighted_data_grid():

    def __init__(self, currency, unit, interval, length):

        # Internal class variables
        self.currency = currency

        # Internal variables for structuring the timeseries
        self.time_unit = unit
        if self.time_unit == 'minutes':
            self.time_unit_divider = 1000 * 60
        elif self.time_unit == 'hours':
            self.time_unit_divider = 1000 * 60 * 60
        elif self.time_unit == 'days':
            self.time_unit_divider = 1000 * 60 * 60 * 24
        self.time_interval = interval
        self.time_length = length

        # Time series data
        self.time_series_grid = {}
