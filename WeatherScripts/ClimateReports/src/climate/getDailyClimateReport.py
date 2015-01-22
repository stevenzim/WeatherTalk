"""Script to get desired weather observations from NWS daily climate reports
	
	Written by: Steven Zimmerman
	Date: Jan 19th  2015

	
	Description: Given a file/list of all NWS stations with daily reports.  This
							script will pull the report for each station and save the daily
							climate data to the specified location
							
	
	Basic steps that occur with this script: 
	0) Open file of reporting stations
	1) For each station code, get the html daily climate report
	2) For each climate report, get the desired reporting values
			and write the value to desired location (e.g. file or db)
	
	
	Requirements:
	1) Internet connection
	2) Input file containing list of NWS offices
	3) Desired values
		a) Date/Time of report
		b) Temperatures - High/Low   Normal/Departure Record? Missing?
		c) Rainfall - Yesterday Total Normal Departure
		d) Snowfall - Yesterday Total Normal Departure
		e) Wind - Highest  Gust Average
		f) Average Sky Cover
		g) Weather Conditions - NOSIG/RAIN/ETC
		h) Humidity - High/Low/Average
		
	Resources (very helpful in creation of script): 
	#http://www.weather.gov
	
	TODO:

	Usage:
	$ python getDailyClimateReports.py
"""


###########################
### import existing modules to use
###########################

import os
import re
import time
import urllib


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
		

###########################
### Main part of program
###########################

recordExists = False
prevMetarDate = '00'	#initialize previous metar date, used to check if file exist
outputFileOpen = False  #used to test if output file is open or not. 
existingMetarRecords = []   #used to store list of metar records associated with file for particular day.  records have ICAO DDHHHHZ format, each metar record will be checked against list

#get gmt Time and create current YYYY-MM-DD string
gmtTime = time.gmtime()
currentDateStamp = str(gmtTime.tm_year) + '-' + checkAddZero(gmtTime.tm_mon) + '-' + checkAddZero(gmtTime.tm_mday)
currentYrMonStamp = str(gmtTime.tm_year) + '-' + checkAddZero(gmtTime.tm_mon)
currentTimeStamp = checkAddZero(gmtTime.tm_hour) +  checkAddZero(gmtTime.tm_min)

#open error file for append and write date time stamp
# oErrorFile = open('errorFile.txt', 'a')
# oErrorFile.write (currentDateStamp + '-' + currentTimeStamp + '\n')




oFile = open('ClimateStations-WithReportHeader.csv' ,'w')
iFile = open('climReportStationList.csv' ,'r')
iFile.readline()  #header
for line in iFile:
	temperatureSection = 0
	stationData = line.split(',')
	stationOfficeCode = stationData[2]
	stationName = stationData[3]  #station name e.g. city
	stationCode = stationData[4]  #station id
	urllib.urlretrieve ('http://www.weather.gov/climate/getclimate.php?date=&wfo=SEW&sid='+ stationCode + '&pil=CLI&recent=yes',"tempDaily.report")
	htmlFile = open('tempDaily.report' ,'r')
	oFile.write(stationOfficeCode + ',' + stationCode + ',' + stationName +  ',')
	for htmlLine in htmlFile:
		if re.search('WEATHER ITEM',htmlLine):
			oFile.write(htmlLine)
		if re.search('TEMPERATURE',htmlLine) and temperatureSection == 0:
			temperatureSection = 1
			print htmlLine
			continue
		if temperatureSection == 1:
			if re.search('MAXIMUM',htmlLine) or re.search('MINIMUM',htmlLine):
				temperatureData = htmlLine.split()
				#oFile.write(temperatureData[1] + ',' + temperatureData[4] +  ','  + temperatureData[6] + ',' + temperatureData[7] + ',' + temperatureData[8] + ',')
				oFile.write(temperatureData[1] + ',')
				print temperatureData
		if re.search('PRECIPITATION',htmlLine):
			temperatureSection = 2
			oFile.write('\n')


			
oFile.close()
			
			
			climateLocation = htmlLine.split('y(')
			climateLocation = climateLocation[1].split(');')
			climateLocation = climateLocation[0].split('\'')
			print officeData
			print climateLocation
			#print climateLocation[0]
			oFile.write(officeData[0] + ',' + officeData[1] +  ','  + officeData[2] + ',')
			oFile.write(climateLocation[1] + ',' + climateLocation[3] + '\n')

			
oFile.close()

		
htmlFile = open('tempDaily.report' ,'r')
oFile.write(stationCode + ',' + stationName +  ',')
for htmlLine in htmlFile:
	if re.search('TEMPERATURE',htmlLine) and temperatureSection == 0:
		temperatureSection = 1
		print htmlLine

temperatureSection = 0		
htmlFile = open('tempDaily.report' ,'r')
oFile.write(stationCode + ',' + stationName +  ',')
for htmlLine in htmlFile:
	if re.search('TEMPERATURE',htmlLine) and temperatureSection == 0:
		temperatureSection = 1
		print htmlLine
		continue
	if temperatureSection == 1:
		if re.search('MAXIMUM',htmlLine) or re.search('MINIMUM',htmlLine):
			temperatureData = htmlLine.split()
			oFile.write(temperatureData[1] + ',' + temperatureData[4] +  ','  + temperatureData[6] + ',' + temperatureData[7] + ',' + temperatureData[8] + ',')
			print temperatureData
	if re.search('PRECIPITATION',htmlLine):
		temperatureSection = 2
		
		
		

