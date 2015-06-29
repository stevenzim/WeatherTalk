#!/usr/bin/env python
#  TODO:  UPDATE--> 
#  A python script to extract and convert desired weather metrics/values from NWS daily climate reports weather files
#  and prepare for database insertion
#
# 
#  Copyright 2015  Steven Zimmerman
# 

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

for more details of how these values are converted, see http://www.ofcm.gov/fmh-1/pdf/L-CH12.pdf
"""

import os
import re
import datetime


def setSunToMins(sunriseString,sunsetString):
    '''Given sunrise/sunset in 759 AM and 804PM format, returns total potential sunshine in minutes'''
    if (sunriseString == None) or  (sunsetString == None):
        return -999
    if (sunriseString == -999) or  (sunsetString == -999):
        return -999
    if (type(sunriseString) != type("")) or  (type(sunsetString) != type("")):
        return -999
    if (len(sunriseString.split(' '))!= 2) or  (len(sunsetString.split(' '))!= 2):
        return -999
    if (sunriseString.split(' ')[1] != 'AM') or  (sunsetString.split(' ')[1] != 'PM'):
        return -999
    amTime = sunriseString.split(' ')[0]
    pmTime = sunsetString.split(' ')[0]
    amLen = len(amTime)

    amHours = (12 - int(amTime[-amLen:-amLen+1]))
    amMins = 60 - int(amTime[-2:])
    amTotal = amHours*60 + amMins
    pmLen = len(pmTime)
    pmHours = (13 - int(pmTime[-pmLen:-pmLen+1]))
    pmMins = int(pmTime[-2:])
    pmTotal = pmHours*60 + pmMins
    return amTotal + pmTotal

def setWindsToKnots(windsInMPH):
    '''Convert wind mph to wind knots'''
    if type(windsInMPH) != type(-999.9):
        return -999.9
    if windsInMPH == -999.9:
        return -999.9
    else:
        return windsInMPH/1.15

def setTempsToCelsius(tempsInF):
    '''Convert temp in F to C'''
    if type(tempsInF) != type(-999.9):
        return -999.9
    if tempsInF == -999.9:
        return -999.9
    else:
        return round(((tempsInF-32.0)/1.8),1)
        

def setDateToDatetime(icaoCode,dateString):
    '''
    Provide icao string and dateString in YYYY-MM-DD
    Returns startTime and endTime in UTC value format YYYY-MM-DD HH:MM:SS
    '''
    #TODO: Get time string from db and add test for wrong icao code
    try:
        startTime = ''
        endTime = ''
        if icaoCode =='KJFK':
            startTime ='05:00:00'
            endTime = '04:59:59'
        if icaoCode =='KSFO':
            startTime ='08:00:00'
            endTime = '07:59:59'
        date = datetime.datetime.strptime(dateString,"%Y-%m-%d")
        dayAhead = date + datetime.timedelta(days = 1)
        endDayString = dayAhead.strftime("%Y-%m-%d")
        startDateTime = dateString + " " + startTime
        endDateTime = endDayString + " " + endTime
        print [startDateTime,endDateTime]
        return [startDateTime,endDateTime]
    except:
        raise ValueError("ICAO code not in station list, or date string not in correct format")



def setFloat(dict,key):
    '''Return 999 to indicate missing'''
    try:
        return float(dict[key])
    except:
        return -999.9

def setBool(dict,key):
    '''Set to integer 1 for true, 0 for false 999 for doesn't exist or missing'''
    try:
        if float(dict[key]):
            return 1
        else:
            return 0
    except:
        return -999


#These are keys that may or may not occur in each report, but they must be dropped
keysToDrop =         ["<type_'float'>",\
                    "<type_'unicode'>",\
                    "observations",\
                    "precipitation_liquid_last",\
                    "precipitation_liquid_normal",\
                    "precipitation_liquid_precipitation",\
                    "precipitation_liquid_record",\
                    "precipitation_liquid_time",\
                    "precipitation_liquid_year",\
                    "precipitation_snowfall_last",\
                    "precipitation_snowfall_normal",\
                    "precipitation_snowfall_record",\
                    "precipitation_snowfall_snowfall",\
                    "precipitation_snowfall_time",\
                    "precipitation_snowfall_year",\
                    "temperature_maximum_last",\
                    "temperature_maximum_maximum",\
                    "temperature_maximum_normal",\
                    "temperature_minimum_minimum",\
                    "temperature_maximum_time",\
                    "temperature_maximum_year",\
                    "temperature_maximum_record",\
                    "temperature_minimum_last",\
                    "temperature_minimum_record",\
                    "temperature_minimum_time",\
                    "temperature_minimum_normal",\
                    "temperature_minimum_year",\
                    "winds_winds"]        


def setClimateDict(climateFlatDict):
    ''''''
    #First get rid of any non-needed keys
    for key in keysToDrop:
        climateFlatDict.pop(key,None)
    
    
"precipitation_liquid_departure" = setFloat(climateFlatDict,"precipitation_liquid_departure")
"precipitation_liquid_new_record" = setBool(climateFlatDict,"precipitation_liquid_new_record")
"precipitation_liquid_observed" = setFloat(climateFlatDict,"precipitation_liquid_observed")
"precipitation_snowfall_departure" = setFloat(climateFlatDict,"precipitation_snowfall_departure")
"precipitation_snowfall_new_record" = setBool(climateFlatDict,"precipitation_snowfall_new_record")
"precipitation_snowfall_observed" = setFloat(climateFlatDict,"precipitation_snowfall_observed")
"report-date" = climateFlatDict["report-date"]
"skies_average_sky_cover" = setFloat(climateFlatDict,"skies_average_sky_cover")
"icao_id" = climateFlatDict["station"]
"sun_sunrise" = climateFlatDict["sun_sunrise"]
"sun_sunset" = climateFlatDict["sun_sunset"]
"temperature_maximum_departure" = setFloat(climateFlatDict,"temperature_maximum_departure")
"temperature_maximum_new_record" = setBool(climateFlatDict,"temperature_maximum_new_record")
"temperature_maximum_observed" = setFloat(climateFlatDict,"temperature_maximum_observed")
"temperature_minimum_departure" = setFloat(climateFlatDict,"temperature_minimum_departure")
"temperature_maximum_new_record" = setBool(climateFlatDict,"temperature_minimum_new_record")
"temperature_minimum_observed" = setFloat(climateFlatDict,"temperature_minimum_observed")
"winds_average_wind_speed" = setFloat(climateFlatDict,"winds_average_wind_speed")
"winds_highest_gust_speed" = setFloat(climateFlatDict,"winds_highest_gust_speed")
"winds_highest_wind_speed" = setFloat(climateFlatDict,"winds_highest_wind_speed")

"two_day_avg_precipitation_liquid_departure" = -999.9
"two_day_avg_precipitation_liquid_observed" = -999.9
"two_day_avg_precipitation_snowfall_departure" = -999.9
"two_day_avg_precipitation_snowfall_observed" = -999.9
"two_day_avg_temperature_maximum_departure" = -999.9
"two_day_avg_temperature_maximum_observed" = -999.9
"two_day_avg_temperature_minimum_departure" = -999.9
"two_day_avg_temperature_minimum_observed" = -999.9
"two_day_avg_winds_average_wind_speed" = -999.9

"three_day_avg_precipitation_liquid_departure" = -999.9
"three_day_avg_precipitation_liquid_observed" = -999.9
"three_day_avg_precipitation_snowfall_departure" = -999.9
"three_day_avg_precipitation_snowfall_observed" = -999.9
"three_day_avg_temperature_maximum_departure" = -999.9
"three_day_avg_temperature_maximum_observed" = -999.9
"three_day_avg_temperature_minimum_departure" = -999.9
"three_day_avg_temperature_minimum_observed" = -999.9
"three_day_avg_winds_average_wind_speed" = -999.9

"seven_day_avg_precipitation_liquid_departure" = -999.9
"seven_day_avg_precipitation_liquid_observed" = -999.9
"seven_day_avg_precipitation_snowfall_departure" = -999.9
"seven_day_avg_precipitation_snowfall_observed" = -999.9
"seven_day_avg_temperature_maximum_departure" = -999.9
"seven_day_avg_temperature_maximum_observed" = -999.9
"seven_day_avg_temperature_minimum_departure" = -999.9
"seven_day_avg_temperature_minimum_observed" = -999.9
"seven_day_avg_winds_average_wind_speed" = -999.9

"thirty_day_avg_precipitation_liquid_departure" = -999.9
"thirty_day_avg_precipitation_liquid_observed" = -999.9
"thirty_day_avg_precipitation_snowfall_departure" = -999.9
"thirty_day_avg_precipitation_snowfall_observed" = -999.9
"thirty_day_avg_temperature_maximum_departure" = -999.9
"thirty_day_avg_temperature_maximum_observed" = -999.9
"thirty_day_avg_temperature_minimum_departure" = -999.9
"thirty_day_avg_temperature_minimum_observed" = -999.9
"thirty_day_avg_winds_average_wind_speed" = -999.9

    return{
        #info about report
        'icao_id' : metarList[0],                # ICAO Code e.g. KSEA
        'observation_time' : metarList[1][:-1] + '+00:00',     # Date and Time in UTC  --> Drop Z at end --> add timezone offset e.g. 2015-05-22T14:02:00
        #temps
        'temp_c' : float(metarList[2]),             # Temp C  38.6
        'dewpoint_c' : float(metarList[3]),         # Dewpoint Temp C 24.5
        #winds
        'wind_dir_degrees' : int(metarList[4]),             # Wind Direction 0-360
        'wind_speed_kt' : int(metarList[5]),                # Wind Speed Knots  11
        'wind_gust_kt' : setWindGust(metarList[5],metarList[6]),                 # Wind Speed Knots  15
        #vis & pressure
        'visibility_statute_mi' : setFloat(metarList[7]),      # Visibility in Statute Miles   24.2
        'altim_in_hg' : float(metarList[8]),                # Pressure in inches of Mercury rounded to 2 decimals    29.92
        #report correct and maintenance indicator
        'corrected' : setBool(metarList[9]),                        # Is report a correction   True
        'maintenance_indicator_on' : setBool(metarList[10]),         # Is the weather station due for maintenance  False
        #present weather values
        #TODO: The following wxtsring fields are a very basic conversion of wxstring, if time, consider a more elegant way to do this
        'wx_string' : presentWxString,                       # TODO: Should I convert this to something else or just leave it as a string, perhaps index it so easily searched in db?   e.g. VCTS +RA
        'precip_rain': precipList[0],     #all four precip types return 0 if not reported. 1 = light, 2 = moderate, 3 = heavy , NOTE: VC for vicinity is assumed to be present weather e.g. 1
        'precip_snow': precipList[1],
        'precip_drizzle': precipList[2],
        'precip_unknown': precipList[3],
        'precip_intensity': max(precipList),   #max intensity of all precip types
        'precip_occuring': True if max(precipList) > 0 else False,
        'thunderstorm': setWxTypeBoolean(presentWxString,['TS']),                       #If TS in string, then tstorm occuring  True/False
        'hail_graupel_pellets': setWxTypeBoolean(presentWxString,['GR','GS','PL']),                        #If any in list then true, else false
        'fog_mist': setWxTypeBoolean(presentWxString,['BR','FG']),                            #If any in list then true, else false
        'tornado': setTornado(remark,presentWxString),
        #precip and pressure from remarks
        'three_hour_pressure_tendency':setThreeHrPressureTendency(remark),
        'one_hour_precip':setOneHrPrecip(remark),
        #Cloud cover
        'transmissivity_clouds' : 9.99,             # TODO: Transmissivity of Clouds based on NRCC paper, a very interesting value, but it will take a while to implement e.g. .96
        'max_cloud_cov' : setMaxCloudCover(metarList[12:20]),                     #Max Cloud Percentage based on METAR standards, for details see function above   e.g. .1275
        #other keys/vals
        'metar_type' : metarList[20],               # Report SPECI or METAR     e.g. METAR/SPECI
        'remark' : setRemark(metarList)                  # String with additional info such as SYNOP code  e.g. AO2 LTG DSNT SE AND S P0004 T01330128
    }


