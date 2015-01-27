import os
import json
from climReport import NWSclimReport
import datetime

stationFile = open('MasterStationList.txt','r')
stationFile.readline() #header
	
for station in stationFile:
	stationDetails = station.split(',')
	report = NWSclimReport.ClimateReport()
	reportLines = report.getReport("sew",stationDetails[1])
	utc_datetime = datetime.datetime.utcnow().strftime("%Y-%m-%d-%HZ")
	fileName = 'data/' + utc_datetime + '-' +stationDetails[4] + '.report'
	outFile =  open(fileName,'w')
	for line in reportLines:
		outFile.write(line)
		outFile.write('\n')
	outFile.close()
	print stationDetails[4]
	
