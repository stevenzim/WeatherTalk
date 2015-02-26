import os
import json
from climReport import NWSclimReport

stationFile = open('MasterStationList.txt','r')
stationFile.readline() #header

outputFileName = '26FEB15.json'
	
for station in stationFile:
	stationDetails = station.split(',')
	report = NWSclimReport.ClimateReport()
	reportLines = report.getReport("sew",stationDetails[1])
	report.getSkyCover()
	report.getWinds()
	report.getTemps()
	report.getPrecipData()
	report.getWxObs()
	report.getSunRiseSet()
#	reportDict = {}
#	masterDict = {}
#	reportDict['SKY'] = report.avg_sky_cvg
#	reportDict['WINDS'] = report.winds
#	masterDict[stationDetails[4]] = reportDict
	json.dump(report.buildOutputDictionary(), open(outputFileName,'a'), sort_keys=True, indent=4, separators=(',', ': '))
	print stationDetails[4]
	
