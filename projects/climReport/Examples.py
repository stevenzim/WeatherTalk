import os
import json
from climReport import NWSclimReport

stationFile = open('MasterStationList.txt','r')
stationFile.readline() #header
for station in stationFile:
	stationDetails = station.split(',')
	report = NWSclimReport.getReport("sew",stationDetails[1])
	skyCover = NWSclimReport.getSkyCover(report)
	json.dump(stationDetails[4], open("t.txt",'a'))
	json.dump(skyCover, open("t.txt",'a'))
	#json.dump('\n', open("t.txt",'a'))
	print stationDetails[4]

	