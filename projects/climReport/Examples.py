import os
import json
from climReport import NWSclimReport

stationFile = open('MasterStationList.txt','r')
stationFile.readline() #header
	
for station in stationFile:
	stationDetails = station.split(',')
	report = NWSclimReport.ClimateReport()
	reportLines = report.getReport("sew",stationDetails[1])
	skyCover = report.getSkyCover()
	skyCover = report.getWinds()
	json.dump(stationDetails[4], open("t.txt",'a'))
	json.dump(report.avg_sky_cvg, open("t.txt",'a'))
	json.dump(report.winds, open("t.txt",'a'))	
	print stationDetails[4]
	