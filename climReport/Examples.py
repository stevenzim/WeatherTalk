import os
import json
from climReport import NWSclimReport

stationFile = open('MasterStationList.txt','r')
stationFile.readline() #header

outputFileName = '14MAR15.json'

#init file TODO: NEED TEST IF IT EXISTS
json.dump([], open(outputFileName,'w'), sort_keys=True, indent=4, separators=(',', ': '))    
for station in stationFile:
    stationDetails = station.split(',')
    report = NWSclimReport.ClimateReport()
    reportLines = report.getReport("sew",stationDetails[1],stationDetails[4])
    report.getSkyCover()
    report.getWinds()
    report.getTemps()
    report.getPrecipData()
    report.getWxObs()
    report.getSunRiseSet()
#    reportDict = {}
#    masterDict = {}
#    reportDict['SKY'] = report.avg_sky_cvg
#    reportDict['WINDS'] = report.winds
#    masterDict[stationDetails[4]] = reportDict
    list = json.loads(open(outputFileName,).read())
    list.append(report.buildOutputDictionary())
    json.dump(list, open(outputFileName,'w'), sort_keys=True, indent=4, separators=(',', ': '))
    print stationDetails[4]
    
