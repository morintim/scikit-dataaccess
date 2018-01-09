# The MIT License (MIT)
# Copyright (c) 2016-2017 Massachusetts Institute of Technology
#
# Authors: Victor Pankratius, Justin Li, Cody Rude
# This software has been created in projects supported by the US National
# Science Foundation and NASA (PI: Pankratius)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# mithagi required Base imports
from skdaccess.framework.data_class import DataFetcherCache, TableWrapper
from skdaccess.utilities.grace_util import readTellusData

# 3rd party imports
import pandas as pd


class DataFetcher(DataFetcherCache):

    def __init__(self, ap_paramList, start_date = None, end_date = None):
        '''
        Construct a Grace Data Fetcher

        @param ap_paramList[geo_point]: AutoList of geographic location tuples (lat,lon)
        @param start_date: Beginning date
        @param end_date: Ending date
        '''

        self.start_date = start_date
        self.end_date = end_date


        self.mascon_url = 'ftp://podaac.jpl.nasa.gov/allData/tellus/L3/mascon/RL05/JPL/CRI/netcdf/GRCTellus.JPL.200204_201706.GLO.RL05M_1.MSCNv02CRIv02.nc'
        self.scale_factor_url = 'ftp://podaac.jpl.nasa.gov/allData/tellus/L3/mascon/RL05/JPL/CRI/netcdf/CLM4.SCALE_FACTOR.JPL.MSCNv01CRIv01.nc'


        super(DataFetcher, self).__init__(ap_paramList)


    def output(self):
        '''
        Create a datawrapper containing GRACE mascon data

        @return Table Datawrapper containing Mascon GRACE data
        '''

        geo_point_list = self.ap_paramList[0]()

        file_list = self.cacheData('mascon', [self.mascon_url, self.scale_factor_url])

        data, metadata = readTellusData(file_list[0], geo_point_list,'lat','lon','lwe_thickness', 'Equivalent Water Thickness', time_name='time',
                                        lat_bounds_name='lat_bounds', lon_bounds_name='lon_bounds')

        unc_data, unc_metadata = readTellusData(file_list[0], geo_point_list,'lat','lon','uncertainty', 'EWT Uncertainty', time_name='time',
                                        lat_bounds_name='lat_bounds', lon_bounds_name='lon_bounds')

        scale_data, scale_metadata = readTellusData(file_list[1], geo_point_list, 'lat', 'lon', 'scale_factor')

        for data_name in data.keys():
            data[data_name] = pd.concat([data[data_name], unc_data[data_name]], axis=1)
            metadata[data_name]['scale_factor'] = scale_data[data_name]


        if self.start_date != None or self.end_date != None:
            for label in data.keys():

                if self.start_date != None:
                    data[label] = data[label][self.start_date:]

                if self.end_date != None:
                    data[label] = data[label][:self.end_date]


        return TableWrapper(data, meta_data=metadata,
                            default_columns=['Equivalent Water Thickness'],
                            default_error_columns=['EWT Uncertainty'])
