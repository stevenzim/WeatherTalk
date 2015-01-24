import urllib
import os
import re


	
def getReport(officeID, climStationID):
	goodReport = False
	reportLines = []
	urllib.urlretrieve ('http://www.weather.gov/climate/getclimate.php?date=&wfo=' + officeID +'&sid='+ climStationID + '&pil=CLI&recent=yes',"tempDaily.report")
	report = open("tempDaily.report" , 'r')
	for line in report:
		if re.search('The chosen WFO ID could not be found in the database', line):
			return {climStationID : officeID + " is wrong WFO office code"}
		if re.search('Sorry, no records are currently available', line):
			return {climStationID : climStationID + " is wrong WFO climate station code"}
		if re.search('<h3>Climatological Report', line):
			goodReport = True
		if goodReport:
			reportLines.append(line.rstrip())
	return reportLines
	
def getSkyCover(reportLines):
	for line in reportLines:
		if re.search('AVERAGE SKY COVER', line):
			startIdx = line.find('AVERAGE')
			lineList = line[startIdx:].split()
			#TODO: add handler for case when value is not a float
			if lineList[3] == 'MM':
				return {'AVERAGE SKY COVER' : 'MISSING'}
			else:
				return {'AVERAGE SKY COVER' : float(lineList[3])}
	return {'AVERAGE SKY COVER' : 'NOT AVAILABLE'}

