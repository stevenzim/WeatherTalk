#######
'''
A simple script to strip out non-desired data from METAR report
This script also removes all non-CONUS reports i.e. only saves reports with station id first char=K
Should be run every 5 minutes due to frequent updating of reports
From here, you can store data in database or whereever

usage/cmdline example to run every 5 minutes: 
'while true; do      python rawMETARcollector.py;     sleep 300; done'
while true
do 
    python rawMETARcollector.py
    sleep 300
done

'''
#######


###########################
### import existing modules to use
###########################

import os
import re
import datetime
import urllib
import csv

from wxtalk import helper
###########################
### user-defined functions
###########################

#function to check if timeValue is a single digit.  If so, then tack on a 0 at front for filename consistency
def checkAddZero(timeValue):
    if timeValue < 10:
        strTimeValue = '0' + str(timeValue)
        return strTimeValue
    else:
        return str(timeValue)
        
def isFloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def outputToCSV(listOfList,outFile):
    with open(outFile, 'wb') as csvfile:
        csvWriter = csv.writer(csvfile)        
        for list in listOfList:
            csvWriter.writerow(list)

###########################
### Main part of program
###########################
#create temp file and permanent output file
#TODO: Need to clean this up so that it works with relative and absolute paths
tempMetarFile = helper.getProjectPath() + "/wxtalk/resources/temp/temp.metar"
dirName = helper.getProjectPath() + '/wxtalk/resources/data/metar/1-raw/'
utc_datetime = datetime.datetime.utcnow().strftime("%Y-%m-%d-%H%MZ")
outFileName = dirName + 'METAR_%s.csv' % utc_datetime


#retrieve data
urllib.urlretrieve ('https://aviationweather.gov/adds/dataserver_current/current/metars.cache.csv',tempMetarFile)

#create header for output file
newHeader = 'station_id,observation_time,temp_c,dewpoint_c,wind_dir_degrees,wind_speed_kt,wind_gust_kt,visibility_statute_mi,altim_in_hg,corrected,maintenance_indicator_on,wx_string,sky_cover,cloud_base_ft_agl,sky_cover,cloud_base_ft_agl,sky_cover,cloud_base_ft_agl,sky_cover,cloud_base_ft_agl,metar_type,remark'
newHeader = newHeader.split(',')

#initialize output list
listToOutput = []
listToOutput.append(newHeader)

#### PROCESS METAR FILE ####
metarReports = open(tempMetarFile,'r')

#read first 6 lines, these will not be written to output file
metarReports.readline() #errors
metarReports.readline() #warnings
metarReports.readline() #retrieval time in ms
metarReports.readline() #type of report
metarReports.readline() #number of results
metarReports.readline() #header

for report in metarReports:
    '''
    Loops through each metar report and loads into output list if all test pass
    '''
    #read in each report from temp file.  Each line = 1 report
    origFields = report.strip().split(',')
    newFields = []
    remark = []
    if origFields[1][0] != 'K':     #Test for only lower 48 METAR
        continue
    if len(origFields) < 40:        #Test to confirm valid metar fields
        continue
    if re.search('RMK',origFields[0]):      #GET Remarks if they exist
        remarksList = origFields[0].split('RMK')
        remark.append(remarksList[1])
    #indexes we want: 1,2,5,6,7,8,9,10,11,13,16,21,22,23,24,25,26,27,28,29,42
    newFields = newFields + origFields[1:3]         #station_id,observation_time
    newFields = newFields + origFields[5:12]        #temp_c,dewpoint_c,wind_dir_degrees,wind_speed_kt,wind_gust_kt,visibility_statute_mi,altim_in_hg
    newFields = newFields + origFields[13:14]       #corrected?
    newFields = newFields + origFields[16:17]        #maintenance_indicator_on?
    newFields = newFields + origFields[21:30]       #skycover details
    newFields = newFields + origFields[42:43]       #report type e.g. METAR,SPECI
    newFields = newFields + remark                 #append remark
    print origFields[1]
    listToOutput.append(newFields)

metarReports.close()

#output to CSV
outputToCSV(listToOutput,outFileName)
