import os
import json
from climReport import NWSclimReport

stationFile = open('MasterStationList.txt','r')
stationFile.readline() #header
	
for station in stationFile:
	stationDetails = station.split(',')
	report = NWSclimReport.ClimateReport()
	reportLines = report.getReport("sew",stationDetails[1])
	report.getSkyCover()
	report.getWinds()
	reportDict = {}
	masterDict = {}
	reportDict['SKY'] = report.avg_sky_cvg
	reportDict['WINDS'] = report.winds
	masterDict[stationDetails[4]] = reportDict
	json.dump(masterDict, open("t.txt",'a'), sort_keys=True, indent=4, separators=(',', ': '))
	print stationDetails[4]
	
