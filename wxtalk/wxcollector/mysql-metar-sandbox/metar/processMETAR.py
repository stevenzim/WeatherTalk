#!/usr/bin/env python
#  TODO:  UPDATE--> 
#  A python package for extracting reported daily climatology from the 
#     US National Weather Service (NWS) daily climate report
# 
#     These products are issued daily and provide information such as hi/lo temps
#  precip/snow totals, observed weather, total cloud cover, etc.
#
#  The NCDC http://www.ncdc.noaa.gov/cdo-web/datasets provides official climate data
#
#  These NWS daily climate reports are unofficial.  However, the reports are still very useful
#  1) They have derived products, such as average cloud cover, which are not easily available from NCDC
#  2) They are relevant for 0000 - 2359 local time, which is important if you want to know the highs and lows specific
#     to the relative time at the location.  WMO (World Meteorological Org) and NCDC data is reported in UTC, with max/mins
#            recorded in the 12Z - 12Z period.  As such, the NWS report is a much more relevant report to people living near the station
#
#  At the moment, all precip and temp values in this report are in inches and fahrenheit respectively, but could be easily convertedValue
#
#  This class has only been tested for the stations in MasterStationList provided in project 
#  The reports for all stations have different formats, this module attempts to handle the dynamic nature of these reports.  
#  There are additonal stations which produce reports not in MasterStationList, however they have been excluded
#  because they are not official WMO/ICAO/METAR stations
#
#  The most recent Climate report for a given station is available at the URL where officeID could be any 3 letter code for offices
#  that issue daily reports and climStationID is 3 letter code for actual station.  See MasterStationList for details
#  http://www.weather.gov/climate/getclimate.php?date=&wfo=' + officeID +'&sid='+ climStationID + '&pil=CLI&recent=yes'
#
# 
#  Copyright 2015  Steven Zimmerman
# 
"""
TODO:  UPDATE--> This module defines the National Weather Service climate report class.  
A Climate Report object represents the weather data deemed most important from the
daily NWS climate report.  A Google search for "NWS Daily Climate Report" will provide examples

SEE Examples-METAR.py for usage


"""

__author__ = "Steven Zimmerman"

__email__ = "szimme@essex.ac.uk"

__version__ = "0.1"

__LICENSE__ = """
Copyright (c) 2015, 
All rights reserved.

Redistribution and use in source and binary forms, 
with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, 
this list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, 
this list of conditions and the following disclaimer in the documentation 
and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, T
HE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. 
IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, 
EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import os
import re
import datetime

        
def setWindGust(windSpeed,windGust):
    '''Set wind gust to wind speed if no wind gust is recorded'''
    if windGust == '':
        return int(windSpeed)
    else:
        return int(windGust)

def setFloat(value):
    '''Return 999 to indicate missing'''
    try:
        return float(value)
    except:
        return 999.

def setBool(value):
    '''Set to False if string is not True'''
    if value:
        return True
    else:
        return False
        
def setRemark(metarList):
    '''Need to handle situation when no remark is included'''
    if len(metarList) < 22:
        return ''
    else:
        return metarList[21]


def getMetarDict(metarList):
    '''Takes in a cleaned up list containing data from METAR
    returns  a dictionary with data in format necessary for database
    there is intentionally no error handling. If an exception is thrown, then
    the data has something missing (e.g. wind/temp data) and thus should not be 
    recorded'''
    return{
    'station_id' : metarList[0],                # ICAO Code
    'observation_time' : metarList[1][:-1],     # Date and Time in UTC  --> Drop Z at end
    'temp_c' : float(metarList[2]),             # Temp C
    'dewpoint_c' : float(metarList[3]),         # Dewpoint Temp C
    'wind_dir_degrees' : int(metarList[4]),             # Wind Direction 0-360
    'wind_speed_kt' : int(metarList[5]),                # Wind Speed Knots
    'wind_gust_kt' : setWindGust(metarList[5],metarList[6]),                 # Wind Speed Knots
    'visibility_statute_mi' : setFloat(metarList[7]),      # Visibility in Statute Miles
    'altim_in_hg' : float(metarList[8]),                # Pressure in inches of Mercury
    'corrected' : setBool(metarList[9]),                        # Is report a correction
    'maintenance_indicator_on' : setBool(metarList[10]),         # Is the weather station due for maintenance
    'wx_string' : 'NONE',                       # TODO: String with Signficant weather
    'transmissivity_clouds' : 999.,             # TODO: Transmissivity of Clouds based on NRCC paper
    'max_cloud_cov' : 999.,                     # TODO: Max Cloud Percentage based on METAR standards
    'metar_type' : metarList[20],               # Report SPECI or METAR
    'remark' : setRemark(metarList),                   # String with additional info such as SYNOP code
    'concat_station_date' : metarList[0] + metarList[1]
    }


