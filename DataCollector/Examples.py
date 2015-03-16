import os
from collectors import helper
from collectors.climReport import NWSclimReport

dataPath = 'data/climate/'      #path to data files
reportList = []         #list storing dictionary reports


stationFile = open('MasterStationList.txt','r')     #master station list of
                                                    # climate stations
stationFile.readline()                              #header


#init file TODO: NEED TEST IF IT EXISTS
stationList = []
for station in stationFile:
    stationList.append(station)
stationFile.close()
#print len(stationList)
from random import shuffle
shuffle(stationList)
#print stationList[1].split(',')[1]

for station in stationList: 
#for station in stationFile:

    #get station details from current line in master list
    #instantiate report object
    #scrap data report data from NWS and load data to object
    stationDetails = station.split(',')
    report = NWSclimReport.ClimateReport()
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
    

    #fullFilePath = dataPath + fileName
    
    #create file if it doesnt exist and load file if it does exist
    #if fileName in listRepoFiles:
    #    print fullFilePath
    #    reportList = helper.loadJSONfromFile(fullFilePath)
    #else:
    #    helper.dumpJSONtoFile(fullFilePath, [])
    
    #run report methods
    report.getSkyCover()
    report.getWinds()
    report.getTemps()
    report.getPrecipData()
    report.getWxObs()
    report.getSunRiseSet()

    #check to see if the report already exists
    #if it does exist, then it needs to be updated
    #assumption is that latest report has most correct data
    # indexToUpdate = None
    # updateReportList = False
    # for i, reportDict in enumerate(reportList):
        # uuid = stationDetails[4] + report.summaryDate
        # if uuid in reportDict:
            # indexToUpdate = i
            # updateReportList = True      
            # print 'update list'
            # break
   
   
    helper.dumpJSONtoFile(stationFullFilePath,report.buildOutputDictionary())
    print stationDetails[4]
    
