"""Script to get list of all National Weather Service(NWS) stations that produce a daily climate report
	
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
### Main part of program
###########################

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


	

