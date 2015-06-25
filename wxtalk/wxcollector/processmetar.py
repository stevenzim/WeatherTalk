#!/usr/bin/env python
#  TODO:  UPDATE--> 
#  A python script to extract desired weather metrics/values from metar weather files
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

skyCoverDict = {"":-999.,"CLR":0.0,"SKC":0.0,"FEW":.1875,"SCT":.4375,"BKN":.75,"OVC":1.0,"OVX":1.0,"VV":1.0}

        
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
        
def setPrecipVals(wxstring,precipCode):
    '''Given metar present wxstring and precipCode to test for,
    returns intensity where 0 = none, 1 = light, 2 = moderate, 3 = heavy
    derived from: http://www.ofcm.gov/fmh-1/fmh1.htm
    '''
    #TODO: Consider a more elegant solution, this is prototype quick code
    intensity = 0
    if precipCode in wxstring:
        intensity = 2
    if intensity > 0:
        if '-' in wxstring:
            intensity = 1
        if '+' in wxstring:
            intensity = 3
    return intensity
    
def setWxTypeBoolean(wxstring,listOfWxCodes):
    '''Given metar present wxstring and list of wx codes to test for,
    returns True if one of the codes occurs in wxstring, else False
    derived from: http://www.ofcm.gov/fmh-1/fmh1.htm
    '''
    for code in listOfWxCodes:
        if code in wxstring:
            return True
    return False    
        
def setMaxCloudCover(sky_cover_fields):
    '''Convert sky cover string to numeric value representing maximum sky cover.  Based on 
    http://www.aviationweather.gov/adds/metars/description/page_no/4 & http://weather.cod.edu/notes/metar.html
    Values are calculated based on mean of max and min e.g. few min = 1/8 few max = 2/8 --> few = 3/16'''
    #TODO: In future consider handling TCU and CB for towering cumulous and cumulonimbus respectively
    max_cloud_cov = -1999.0
    for count, skyCoverString in enumerate(sky_cover_fields):
        #mod to extract only even vals of list passed in.  They come in pairs of sky_cover,above_ground_level
        if (count % 2) == 0:   
            curSkyVal = skyCoverDict[skyCoverString]
            if curSkyVal > max_cloud_cov:
                max_cloud_cov = curSkyVal
    return max_cloud_cov
        
def setRemark(metarList):
    '''Need to handle situation when no remark is included'''
    if len(metarList) < 22:
        return ''
    else:
        return metarList[21]

def setOneHrPrecip(remark):
    '''provided remark string, finds one hour precip value and converts to desired output.  We want none if there is nothing there or error'''
    match = re.search('P\d\d\d\d', remark)
    if match != None:
        precip = match.group(0)
        precip = precip[1:]
        precip = precip[:2] +  "." +  precip[2:]
        try:
            precip = round(float(precip),2)
            return precip
        except:
            return -999.
    return -999.

def setThreeHrPressureTendency(remark):
    '''provided remark string, finds three hour pressure tendency and converts to desired output.  We want none if there is nothing there or error'''
    match = re.search('5\d\d\d\d', remark)
    if match != None:
        pressure = match.group(0)
        try:
            change = float(pressure[2:4] +  "." +  pressure[4])
            change = round(change,1)
            tendencyCode = int(pressure[1])
        except:
            return -999.
        if tendencyCode >3:
            return change
        if change == 0.00:
            return change
        if tendencyCode < 4:
            return -change
    return -999.   

def setTornado(remark,presentWxString):
    '''TEST to determine if tornado/funnel cloud has been reported'''
    if setWxTypeBoolean(presentWxString,['FC']):
        return True
    if 'TORNADO' in remark:
        return True
    if 'FUNNEL CLOUD' in remark:
        return True
    if 'WATERSPOUT' in remark:
        return True
    return False

def getMetarDict(metarList):
    '''Takes in a cleaned up list containing data from METAR
    returns  a dictionary with data in format necessary for use in other processing, e.g. entry into SQL database
    there is intentionally no error handling. NOTE: --> If an exception is thrown, then
    the data has key information missing (e.g. wind/temp data) and thus should not be 
    recorded'''
    presentWxString = metarList[11]
    precipList = [setPrecipVals(presentWxString,'RA'),\
                    setPrecipVals(presentWxString,'SN'),\
                    setPrecipVals(presentWxString,'DZ'),\
                    setPrecipVals(presentWxString,'UP')]
    remark = setRemark(metarList)
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


