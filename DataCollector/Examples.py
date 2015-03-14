import os
from collectors import helper
from collectors.climReport import NWSclimReport

dataPath = 'data/'      #path to data files
reportList = []         #list storing dictionary reports


stationFile = open('MasterStationList.txt','r')     #master station list of
                                                    # climate stations
stationFile.readline()                              #header


#init file TODO: NEED TEST IF IT EXISTS
#helper.dumpJSONtoFile(outputFileName , [])

 
for station in stationFile:

    #get station details from current line in master list
    #instantiate report object
    #scrap data report data from NWS and load data to object
    stationDetails = station.split(',')
    report = NWSclimReport.ClimateReport()
    reportLines = report.getReport("sew",stationDetails[1],stationDetails[4])
    
    #file checker
    listRepoFiles = helper.getListOfFiles(dataPath)
    fileName = report.summaryDate + '.json'
    fullFilePath = dataPath + fileName
    
    #create file if it doesnt exist and load file if it does exist
    if fileName in listRepoFiles:
        reportList = helper.loadJSONfromFile(fullFilePath)
    else:
        helper.dumpJSONtoFile(fullFilePath, [])
    
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
    indexToUpdate = None
    updateReportList = False
    for i, reportDict in enumerate(reportList):
        uuid = stationDetails[4] + report.summaryDate
        if uuid in reportDict:
            indexToUpdate = i
            updateReportList = True      
            print 'update list'
            break
    
    #if list neeed updating then update, otherwise append with new report
    if updateReportList:
        reportList[indexToUpdate] = report.buildOutputDictionary()
    else:
        reportList.append(report.buildOutputDictionary())
    
    #TODO: DANGER!!!!! What happens if program craps out while list still loaded???????????????????????
    
    #write report list to JSON
    helper.dumpJSONtoFile(fullFilePath, reportList)
    print stationDetails[4]
    
