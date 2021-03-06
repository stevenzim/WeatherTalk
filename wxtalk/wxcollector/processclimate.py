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
import flatdict

from wxtalk import helper
from wxtalk.db import dbfuncs as db

import os
import os.path
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


def setDepartFromNormCelsius(tempsInF):
    '''Convert temp in F to C'''
    if type(tempsInF) != type(-999.9):
        return -999.9
    if tempsInF == -999.9:
        return -999.9
    else:
        return round((tempsInF/1.8),1)        

def setDateToDatetime(icaoCode,dateString):
    '''
    Provide icao string and dateString in YYYY-MM-DD
    Returns startTime and endTime in UTC value format YYYY-MM-DD HH:MM:SS
    '''
    #TODO: Get time string from db and add test for wrong icao code
    try:
        startTime = ''
        endTime = ''
        s = db.Connector()
        sqlstring = 'SELECT daily_report_start_time_utc, daily_report_end_time_utc FROM weather.stations\
                    WHERE icao_id = \'' + icaoCode + '\''
        s.cursor.execute(sqlstring)
        stationDetails = s.cursor.fetchone()
        startTime =stationDetails[0]
        endTime = stationDetails[1]   
        date = datetime.datetime.strptime(dateString,"%Y-%m-%d")
        dayAhead = date + datetime.timedelta(days = 1)
        endDayString = dayAhead.strftime("%Y-%m-%d")
        startDateTime = dateString + " " + startTime
        endDateTime = endDayString + " " + endTime
        #print [startDateTime,endDateTime]
        return [startDateTime,endDateTime]
    except Exception as error:
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
        
    datesTimes = setDateToDatetime(climateFlatDict["station"],climateFlatDict["report-date"])
    
    return{"icao_id" : climateFlatDict["station"],
            "report_date" : climateFlatDict["report-date"],
        "precipitation_liquid_departure" : setFloat(climateFlatDict,"precipitation_liquid_departure"),
        "precipitation_liquid_new_record" : setBool(climateFlatDict,"precipitation_liquid_new_record"),
        "precipitation_liquid_observed" : setFloat(climateFlatDict,"precipitation_liquid_observed"),
        "precipitation_snowfall_departure" : setFloat(climateFlatDict,"precipitation_snowfall_departure"),
        "precipitation_snowfall_new_record" : setBool(climateFlatDict,"precipitation_snowfall_new_record"),
        "precipitation_snowfall_observed" : setFloat(climateFlatDict,"precipitation_snowfall_observed"),
        "skies_average_sky_cover" : setFloat(climateFlatDict,"skies_average_sky_cover"),
        "total_sun_potential" : setSunToMins(climateFlatDict["sun_sunrise"],climateFlatDict["sun_sunset"]),
        "temperature_maximum_departure" : setDepartFromNormCelsius((setFloat(climateFlatDict,"temperature_maximum_departure"))),
        "temperature_maximum_new_record" : setBool(climateFlatDict,"temperature_maximum_new_record"),
        "temperature_maximum_observed" : setTempsToCelsius(setFloat(climateFlatDict,"temperature_maximum_observed")),
        "temperature_minimum_departure" : setDepartFromNormCelsius((setFloat(climateFlatDict,"temperature_minimum_departure"))),
        "temperature_minimum_new_record" : setBool(climateFlatDict,"temperature_minimum_new_record"),
        "temperature_minimum_observed" : setTempsToCelsius(setFloat(climateFlatDict,"temperature_minimum_observed")),
        "winds_average_wind_speed" : round(setWindsToKnots(setFloat(climateFlatDict,"winds_average_wind_speed")),1),
        "winds_highest_gust_speed" : round(setWindsToKnots(setFloat(climateFlatDict,"winds_highest_gust_speed")),1),
        "winds_highest_wind_speed" : round(setWindsToKnots(setFloat(climateFlatDict,"winds_highest_wind_speed")),1),
        "report_start_datetime": datesTimes[0],
        "report_end_datetime": datesTimes[1],
        
        "avg_two_day_precipitation_liquid_departure" : -999.9,
        "avg_two_day_precipitation_liquid_observed" : -999.9,
        "avg_two_day_precipitation_snowfall_departure" : -999.9,
        "avg_two_day_precipitation_snowfall_observed" : -999.9,
        "avg_two_day_temperature_maximum_departure" : -999.9,
        "avg_two_day_temperature_maximum_observed" : -999.9,
        "avg_two_day_temperature_minimum_departure" : -999.9,
        "avg_two_day_temperature_minimum_observed" : -999.9,
        "avg_two_day_winds_average_wind_speed" : -999.9,
        "avg_two_day_skies_average_sky_cover" : -999.9,
        
        "avg_three_day_precipitation_liquid_departure" : -999.9,
        "avg_three_day_precipitation_liquid_observed" : -999.9,
        "avg_three_day_precipitation_snowfall_departure" : -999.9,
        "avg_three_day_precipitation_snowfall_observed" : -999.9,
        "avg_three_day_temperature_maximum_departure" : -999.9,
        "avg_three_day_temperature_maximum_observed" : -999.9,
        "avg_three_day_temperature_minimum_departure" : -999.9,
        "avg_three_day_temperature_minimum_observed" : -999.9,
        "avg_three_day_winds_average_wind_speed" : -999.9,
        "avg_three_day_skies_average_sky_cover" : -999.9,
        
        "avg_seven_day_precipitation_liquid_departure" : -999.9,
        "avg_seven_day_precipitation_liquid_observed" : -999.9,
        "avg_seven_day_precipitation_snowfall_departure" : -999.9,
        "avg_seven_day_precipitation_snowfall_observed" : -999.9,
        "avg_seven_day_temperature_maximum_departure" : -999.9,
        "avg_seven_day_temperature_maximum_observed" : -999.9,
        "avg_seven_day_temperature_minimum_departure" : -999.9,
        "avg_seven_day_temperature_minimum_observed" : -999.9,
        "avg_seven_day_winds_average_wind_speed" : -999.9,
        "avg_seven_day_skies_average_sky_cover" : -999.9,
        
        "avg_thirty_day_precipitation_liquid_departure" : -999.9,
        "avg_thirty_day_precipitation_liquid_observed" : -999.9,
        "avg_thirty_day_precipitation_snowfall_departure" : -999.9,
        "avg_thirty_day_precipitation_snowfall_observed" : -999.9,
        "avg_thirty_day_temperature_maximum_departure" : -999.9,
        "avg_thirty_day_temperature_maximum_observed" : -999.9,
        "avg_thirty_day_temperature_minimum_departure" : -999.9,
        "avg_thirty_day_temperature_minimum_observed" : -999.9,
        "avg_thirty_day_winds_average_wind_speed" : -999.9,
        "avg_thirty_day_skies_average_sky_cover" : -999.9
    }

 
avg_key_days_str =["avg_two_day_",\
        "avg_three_day_",\
        "avg_seven_day_",\
        "avg_thirty_day_" ]  
avg_key_types_str =["precipitation_liquid_departure",\
        "precipitation_liquid_observed",\
        "precipitation_snowfall_departure",\
        "precipitation_snowfall_observed",\
        "temperature_maximum_departure",\
        "temperature_maximum_observed",\
        "temperature_minimum_departure",\
        "temperature_minimum_observed",\
        "winds_average_wind_speed",\
        "skies_average_sky_cover"]




def processAndAggregate():
    '''
    Takes all raw climate daily reports in sepecified input directory and converts keys and values to desired format.
    Desired format includes converstion to units, aggregation of days, etc.
    Outputs combined reports for each station to outdir
    NOTE: This was written while I was sick, the code is very spaghetti like, if time permits I will come back and refactor.  
    I have manually verified the output for several stations and daily conversions and aggregate versions look correct
    '''
    #get all file names and build base dictionary (each station is represented by ICAO.json and values are list of all reports       

    #outdir = '/home/steven/Desktop/T/WeatherTalk/wxtalk/wxcollector/tests/test-data'
    #datadir = outdir +  "/climate"
    filenum = 0
    outdir = helper.getProjectPath() + '/wxtalk/resources/data/climateClean'
    datadir = helper.getProjectPath() + '/wxtalk/resources/data/climate'
    files = []
    stationsDict = {} 
    for dirpath, dirnames, filenames in os.walk(datadir):
        for filename in [f for f in filenames if f.endswith(".json")]:
            files.append( os.path.join(dirpath, filename))
            stationsDict[filename] = []
            filenum += 1
            if (filenum % 100) == 0:
                print filenum

    files.sort() #sort files
    files.reverse() #reverse to make it easier to aggregrate

    #load each daily report to appropriate station key list
    #put key names in correct format
    for file in files:
        stationCode = file.split('/')[-1].split('.')[0]
        print stationCode
        if stationCode[0] == 'P':
            continue
        #try:
        climDict = helper.loadJSONfromFile(file)
        #print climDict
        flatWxDict = flatdict.FlatDict(climDict[climDict.keys()[0]])
        outputDict = {}
        keysList = flatWxDict.keys()
        for key in keysList:
            outputDict[key.replace(':','_').replace(' ','_').lower()]=(flatWxDict[key])
            
        #get desired values for output dict
        outputDict = setClimateDict(outputDict)
        stationsDictKeyName = file.split('/')[-1]  #retrieve original file name e.g. 'KSEA.json' this is the key name
        stationsDict[stationsDictKeyName].append(outputDict)

            

    #update each field to correct output format
    #output each list of dicts of each station to a json file    
    for key in stationsDict:   
        helper.dumpJSONtoFile(outdir +'/' + key,stationsDict[key])
        
        
    aggregrateStations ={}
    count = 0
    for station in stationsDict:
        count += 1
        print station
        print count
        outStation = []
        reports = stationsDict[station]
        stationsSliced = stationsDict[station]
        for report in reports:
            outReport = report
            avg2list=stationsSliced[:2]
            avg3list=stationsSliced[:3]
            avg7list=stationsSliced[:7]
            avg30list=stationsSliced[:30]
            for key in avg_key_types_str:
                #TODO: add in check here for difference between date of first report and last report
                #     if difference doesn't match, then put 999's else sum and average
                #TWO DAY AVERAGE   
                firstDate = datetime.datetime.strptime(avg2list[0]["report_date"],"%Y-%m-%d")
                lastDate = datetime.datetime.strptime(avg2list[-1]["report_date"],"%Y-%m-%d")
                totalDays = firstDate - lastDate
                deltaDays = totalDays.days
                #print avg2list
                if deltaDays < 1:
                    for keyname in avg_key_types_str:
                        avgKeyName = "avg_two_day_" + keyname
                        outReport[avgKeyName] = -999.9
                else:
                    for keyname in avg_key_types_str:
                        avgKeyName = "avg_two_day_" + keyname
                        currentSum = 0
                        for subReport in avg2list:
                            if subReport[keyname] <= -999:
                                currentSum = -999.9
                                break
                            else:
                                currentSum += subReport[keyname]
                        if currentSum <= -999.9:
                            outReport[avgKeyName] = -999.9
                        else:
                            if ("temperature" in keyname) or "wind" in keyname:
                                outReport[avgKeyName] = round((currentSum / 2.),1)
                            else:    
                                outReport[avgKeyName] = round((currentSum / 2.),2)
                #THREE DAY AVERAGE   
                firstDate = datetime.datetime.strptime(avg3list[0]["report_date"],"%Y-%m-%d")
                lastDate = datetime.datetime.strptime(avg3list[-1]["report_date"],"%Y-%m-%d")
                totalDays = firstDate - lastDate
                deltaDays = totalDays.days
                if deltaDays < 2:
                    for keyname in avg_key_types_str:
                        avgKeyName = "avg_three_day_" + keyname
                        outReport[avgKeyName] = -999.9
                else:
                    for keyname in avg_key_types_str:
                        avgKeyName = "avg_three_day_" + keyname
                        currentSum = 0
                        for subReport in avg3list:
                            if subReport[keyname] <= -999:
                                currentSum = -999.9
                                break
                            else:
                                currentSum += subReport[keyname]
                        if currentSum <= -999.9:
                            outReport[avgKeyName] = -999.9
                        else:
                            if ("temperature" in keyname) or "wind" in keyname:
                                outReport[avgKeyName] = round((currentSum / 3.),1)
                            else:    
                                outReport[avgKeyName] = round((currentSum / 3.),2)
                #SEVEN DAY AVERAGE   
                firstDate = datetime.datetime.strptime(avg7list[0]["report_date"],"%Y-%m-%d")
                lastDate = datetime.datetime.strptime(avg7list[-1]["report_date"],"%Y-%m-%d")
                totalDays = firstDate - lastDate
                deltaDays = totalDays.days
                if deltaDays < 6:
                    for keyname in avg_key_types_str:
                        avgKeyName = "avg_seven_day_" + keyname
                        outReport[avgKeyName] = -999.9
                else:
                    for keyname in avg_key_types_str:
                        avgKeyName = "avg_seven_day_" + keyname
                        currentSum = 0
                        for subReport in avg7list:
                            if subReport[keyname] <= -999:
                                currentSum = -999.9
                                break
                            else:
                                currentSum += subReport[keyname]
                        if currentSum <= -999.9:
                            outReport[avgKeyName] = -999.9
                        else:
                            if ("temperature" in keyname) or "wind" in keyname:
                                outReport[avgKeyName] = round((currentSum / 7.),1)
                            else:    
                                outReport[avgKeyName] = round((currentSum / 7.),2)
                #THIRTY DAY AVERAGE   
                firstDate = datetime.datetime.strptime(avg30list[0]["report_date"],"%Y-%m-%d")
                lastDate = datetime.datetime.strptime(avg30list[-1]["report_date"],"%Y-%m-%d")
                totalDays = firstDate - lastDate
                deltaDays = totalDays.days
                if deltaDays < 29:
                    for keyname in avg_key_types_str:
                        avgKeyName = "avg_thirty_day_" + keyname
                        outReport[avgKeyName] = -999.9
                else:
                    for keyname in avg_key_types_str:
                        avgKeyName = "avg_thirty_day_" + keyname
                        currentSum = 0
                        for subReport in avg30list:
                            if subReport[keyname] <= -999:
                                currentSum = -999.9
                                break
                            else:
                                currentSum += subReport[keyname]
                        if currentSum <= -999.9:
                            outReport[avgKeyName] = -999.9
                        else:
                            if ("temperature" in keyname) or "wind" in keyname:
                                outReport[avgKeyName] = round((currentSum / 30.),1)
                            else:    
                                outReport[avgKeyName] = round((currentSum / 30.),2)         
            stationsSliced = stationsSliced[1:]
            outStation.append(outReport)
        aggregrateStations[station] = outStation

        
    #update each field to correct output format
    #output each list of dicts of each station to a json file    
    for key in aggregrateStations:   
        helper.dumpJSONtoFile(outdir +'/' + key,aggregrateStations[key])    


def loadClimateReportsToDB():
    '''Function to load all prepped climate reports into database.  To be run after processAndAggregate() function in above'''
    datadir = helper.getProjectPath() + '/wxtalk/resources/data/climate/Clean'
    files = []
    for dirpath, dirnames, filenames in os.walk(datadir):
        for filename in [f for f in filenames if f.endswith(".json")]:
            files.append( os.path.join(dirpath, filename))


    files.sort() #sort files

    for file in files:
        listOfClimDicts = helper.loadJSONfromFile(file)
        print file.split('/')[-1]
        for climReport in listOfClimDicts:
            try:
                s = db.ClimateReport()
                s.loadClimateReport(climReport)
            except Exception as error:
                print error      
