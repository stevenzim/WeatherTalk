#script to download NWS daily climate reports and store in a local directory structure for later processing
import os
from wxtalk import helper
from wxtalk.wxcollector.collectors.climReport import NWSclimReport

dataPath = helper.getProjectPath() + '/wxtalk/resources/data/climate/'      #path to data files
reportList = []         #list storing dictionary reports


stationFile = open(helper.getProjectPath() + '/wxtalk/resources/WeatherStations/ClimMasterStationList.csv','r')     #master station list of
                                                    # climate stations
stationFile.readline()                              #header


# randomly shuffle to handle network dropping and not miss reports
stationList = []
for station in stationFile:
    stationList.append(station)
stationFile.close()
from random import shuffle
shuffle(stationList)


for station in stationList: 
#for station in stationFile:

    #get station details from current line in master list
    #instantiate report object
    #scrape data report data from NWS and load data to object
    stationDetails = station.split(',')
    report = NWSclimReport.ClimateReport()
    #TODO: Add feature to check for date match, if report date is for current day
    #       then we don't want it yet.  It should be for yesterday or before.
    #       i.e. We only want complete reports
    reportLines = report.getReport("sew",stationDetails[1],stationDetails[4])
    
    #file checker
    
    fileName = report.summaryDate + '.json'
    stationFileName = stationDetails[4] + '.json'
    
    fullDirPath = dataPath + report.summaryDate +'/'


    if not os.path.exists(fullDirPath):
        os.makedirs(fullDirPath)    
    listRepoFiles = helper.getListOfFiles(fullDirPath)
    fullFilePath = fullDirPath + fileName
    stationFullFilePath = fullDirPath + stationFileName
    
 
    #run report methods
    report.getSkyCover()
    report.getWinds()
    report.getTemps()
    report.getPrecipData()
    report.getWxObs()
    report.getSunRiseSet()


   
   
    helper.dumpJSONtoFile(stationFullFilePath,report.buildOutputDictionary())
    print stationDetails[4]
    
