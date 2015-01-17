###########################
### import existing modules to use
###########################

import os
import re
import time
import urllib



#0	tm_year	(for example, 1993)
#1	tm_mon	range [1, 12]
#2	tm_mday	range [1, 31]
#3	tm_hour	range [0, 23]
#4	tm_min	range [0, 59]
#5	tm_sec	range [0, 61]; see (2) in strftime() description
#6	tm_wday	range [0, 6], Monday is 0
#7	tm_yday	range [1, 366]
#8	tm_isdst	0, 1 or -1; see below

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
oErrorFile = open('errorFile.txt', 'a')
oErrorFile.write (currentDateStamp + '-' + currentTimeStamp + '\n')

#retrieve and save current metar csv file
urllib.urlretrieve ('https://aviationweather.gov/adds/dataserver_current/current/metars.cache.csv',"temp.metar")



#check if file exists and create if it does not  (could become a generic function)
# would be nice to have if statement as negative i.e. if path does not exist
if os.path.exists(currentDateStamp + '.metar'):
	pass
else:
	newFile = open(currentDateStamp + '.metar' , 'w')
	newFile.close()

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