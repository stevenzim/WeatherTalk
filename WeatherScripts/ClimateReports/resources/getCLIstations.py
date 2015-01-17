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
			oFile.write(climateLocation[1] + ',' + climateLocation[4] + '\n')

			
oFile.close()

oFile = open('climReportStationList.csv' ,'w')
htmlFile = open('temp.CLI' ,'r')
for htmlLine in htmlFile:
	if re.search('cliPointArray\[',htmlLine):
		climateLocation = htmlLine.split('(')
		climateLocation = climateLocation[1].split(')')
		climateLocation = climateLocation[0].split('\'')
		print climateLocation[0]
		oFile.write(climateLocation[0] + ',' + climateLocation[1] + '\n')
		
		

oFile.close()
		
htmlFile = open('temp.CLI' ,'r')		
for htmlLine in htmlFile:
	if re.search('cliPointArray\[',htmlLine):
		temp1 = htmlLine.split('(')
		temp2 = temp1[1].split(')')
		climateLocation = temp2[0].split('\'')
		# oFile.write(climateLocation[0])	
		print temp1
		print temp2
		print climateLocation
		print climateLocation[0]
	

officeList = ['LSX','SEW','PQR']

#retrieve and save current metar csv file
for CODE in officeList:
	urllib.urlretrieve ('http://www.weather.gov/climate/index.php?wfo='+ CODE,"temp.CLI")



#check if file exists and create if it does not  (could become a generic function)
# would be nice to have if statement as negative i.e. if path does not exist
# if os.path.exists(currentDateStamp + '.metar'):
	# pass
# else:
	# newFile = open(currentDateStamp + '.metar' , 'w')
	# newFile.close()

###########open temp metar file 
########### and run through file
tempMetarFile = open('temp.metar','r')

#read in first 6 file header lines
error = tempMetarFile.readline()	#error line
warning = tempMetarFile.readline()	#warning line
#check lines 1 and 2 for errors and warnings, if exists then write to error file
if re.match('No',error) or re.match('No',warning):
	pass
else:
	oErrorFile.write(error + ' ' + warning + '\n')
tempMetarFile.readline()	
tempMetarFile.readline()	
tempMetarFile.readline()	
tempMetarFile.readline()	#file header line

#now we are on first metar record and can begin processing
int = 1
for line in tempMetarFile:

	#double check that line has atleast 12 characters, if it isn't, then dump to error file and go to next line
	if len(line) < 13:
		oErrorFile.write(line)
		continue
	
	#sometimes a double quote is in metar string.  This function removes the double quotes in first character
	firstCharacter = line [0:1]
	if re.match('"',firstCharacter):
		line = line[1:]
	
	#get substrings of current metar line, necessary to test if metar line is a duplicate or error and then save appropriately
	currentMetarHeader = line[0:12]		#this is the station and day with time, used to check for duplicate records in existing files  ex: 'KSEA 201045Z'
	metarStation = line[0:4]			#this is the station, could be used for error checking ex: 'KSEA'
	metarDateTime = line[5:11]			#this is the date time DDTTTT, needed for error checking  ex:'201045'  
	currentMetarDate = line[5:7]		#this is the date DD, needed to check if corresponding metar file is open
	currentMetarTime = line[7:11]				#time to compare difference and verify metar is not an error
	metarZ = line[11:12]				#this is the letter Z, hopefully
	
	#error handling break out of current iteration if confirmed not a metar record 
	# 2 checks good enough?????
	#TODO: Add another check for date.  If date is greater than current day, then discard and report to error log

	# 1st check = if datetime is not a float, then its not a METAR record
	if isFloat(metarDateTime):
		pass
	else:
		oErrorFile.write(line)
		continue

	# 2nd check = if metarZ does not = Z
	if re.match('Z',metarZ):
		pass
	else:
		oErrorFile.write(line)
		continue	

	# 3rd check.  Does metar report have a date and time more than 3 minutes ahead of current date time?
	# If date and time is greater than current day and greater than 3 minutes difference, then discard and report to error log
	if (float(currentMetarDate) - float(gmtTime.tm_mday)) > 0 and (float(currentMetarTime) - float(currentTimeStamp)) > 3:
		oErrorFile.write(line)
		continue
	
	# if the current metar record has same date as previous one, then continue working with current output file, else switch to correct date
	if currentMetarDate == prevMetarDate:
		#need to print only records that don't already exist. 	
		if currentMetarHeader in existingMetarRecords:
			continue
		else:
			oFile.write(line)

	else:
		#get current file name
		currentFile = currentYrMonStamp + '-' + currentMetarDate + '.metar'
		# if statement to handle situation where date changes.  Would need to close current file and open different one
		if outputFileOpen:
			oFile.close()
			oFile = open(currentFile ,'r + a')
		else:
			oFile = open(currentFile ,'r + a')
			outputFileOpen = True
		
		#loop through file to get existing metarHeader i.e. ICAO and date combo  and store in list:
		for line in oFile:
			existingMetarHeader = line[0:12]
			existingMetarRecords.append(existingMetarHeader)
		
		#check current metar is in list and print to output file
		if currentMetarHeader in existingMetarRecords:
			continue
		else:
			oFile.write(line)
		

	prevMetarDate = currentMetarDate
	
	int = int + 1

oFile.close()
oErrorFile.close()