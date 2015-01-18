"""Script to run get list of all National Weather Service(NWS) stations that produce a daily climate report
	
	Written by: Steven Zimmerman
	Date: Jan 17th  2015

	
	Description: Given a file/list of all NWS weather forecast offices, this 
							script outputs a list of all stations with daily climate reports.  
							Some stations may be reported on by more than one forecast office,
							as such, manual de-duplication is used after running this script.
							CLI is the NWS code for daily climate report
							
	
	Basic steps that occur with this script: 
	0) Open file of offices
	1) For each office code, get the html climate page
	2) For each climate page, get the weather station name and code
	3) For each weather station name/code --->
		a) concatenate data with office code
		b) output to file
	
	
	Requirements:
	1) Internet connection
	2) Input file containing list of NWS offices
		
	Resources (very helpful in creation of script): 
	#http://www.weather.gov
	
	TODO:

	Usage:
	$ python getCLIstations.py
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
# def checkAddZero(timeValue):
	# if timeValue < 10:
		# strTimeValue = '0' + str(timeValue)
		# return strTimeValue
	# else:
		# return str(timeValue)
		

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

oFile = open('climReportStationList.csv' ,'w')
iFile = open('NWSofficeList.csv' ,'r')
iFile.readline()  #header
for line in iFile:
	officeData = line.split(',')
	outputList = officeData[:3]
	officeCode = officeData[2]  #station id
	urllib.urlretrieve ('http://www.weather.gov/climate/index.php?wfo='+ officeCode,"temp.CLI")
	htmlFile = open('temp.CLI' ,'r')
	oFile.write(officeData[0] + ',' + officeData[1] +  ','  + officeData[2] + ',HEADER,HEADER\n')
	for htmlLine in htmlFile:
		if re.search('cliPointArray\[',htmlLine):
			climateLocation = htmlLine.split('y(')
			climateLocation = climateLocation[1].split(');')
			climateLocation = climateLocation[0].split('\'')
			print officeData
			print climateLocation
			#print climateLocation[0]
			oFile.write(officeData[0] + ',' + officeData[1] +  ','  + officeData[2] + ',')
			oFile.write(climateLocation[1] + ',' + climateLocation[3] + '\n')

			
oFile.close()

# oFile = open('climReportStationList.csv' ,'w')
# htmlFile = open('temp.CLI' ,'r')
# for htmlLine in htmlFile:
	# if re.search('cliPointArray\[',htmlLine):
		# climateLocation = htmlLine.split('(')
		# climateLocation = climateLocation[1].split(')')
		# climateLocation = climateLocation[0].split('\'')
		# print climateLocation[0]
		# oFile.write(climateLocation[0] + ',' + climateLocation[1] + '\n')
		
		

# oFile.close()
		
# htmlFile = open('temp.CLI' ,'r')		
# for htmlLine in htmlFile:
	# if re.search('cliPointArray\[',htmlLine):
		# temp1 = htmlLine.split('(')
		# temp2 = temp1[1].split(')')
		# climateLocation = temp2[0].split('\'')
		# # oFile.write(climateLocation[0])	
		# print temp1
		# print temp2
		# print climateLocation
		# print climateLocation[0]
	

