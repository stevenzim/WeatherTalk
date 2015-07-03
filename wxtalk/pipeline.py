#author: Steven Zimmerman
#created: 10-JUN-2015
#module including key processing pipeline functionality
#TODO: move stuff over from wxtalk.models.twxeety.pipeline.py
#TODO: Consider splitting these functions into classes or seperate files underneath a pipeline folder

from wxtalk.wxcollector import processmetar as metar
from wxtalk import helper
from wxtalk.db import dbfuncs as db
import sys
import os
import math

import logging

import time

# set up logging to file - see previous section for more details
#from: https://docs.python.org/2/howto/logging-cookbook.html
#TODO: Need to learn how to deal with error logging better.  Currently everything is dumping to db.log
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename = os.path.join(helper.getProjectPath(),'wxtalk/errors/db.log'),
                    filemode='a')

logger1 = logging.getLogger('wxtalk.batchLoadMetarReports')


#path to error directory
pathToErrorDir = os.path.join(helper.getProjectPath(),'wxtalk/errors/')

############### METAR PIPE ####################
#STEP 1
def removeDuplicateMetar(rawMetarDir = os.path.join(helper.getProjectPath(),'wxtalk/resources/data/metar/1-raw/'),\
                        filesPerBatch = 250):
    '''
    Purpose of this function: METAR Reports updated by the ADDS(aviation digital data server), 
    these files contain all reports over previous hour or so.  Most stations only update every hour unless if conditions change.
    As such, many files contain nearly 90% duplicate reports.  To speed up insertion into database it is best to remove duplicate
    metar records.  
    The input is a directory containing non-deduped files
    The output is to a sub-directory of this input directory named "deduped"
    '''                    
    #get all non dedupiclate files and sort in logical order
    filesInQueue = helper.getListOfFiles(rawMetarDir)
    filesInQueue.sort()
    
    #initialize counters and print some useful info
    totalFiles = len(filesInQueue)
    totalBatches =  int(math.ceil(float(totalFiles)/float(filesPerBatch)))
    print str(totalFiles) + " files to dedupe in " + str(totalBatches)   + " total batches"
    inFilesProcessed = 0
    batchesComplete = 0
    
    #deduplicate metar reports
    while inFilesProcessed < totalFiles:
        #we process filesPerBatch files at a time
        currentQueue = filesInQueue[:filesPerBatch]
        #process currentQueue and deduplicate all metar in files
        metarDict = {}
        for file in currentQueue:
            inFile = open(rawMetarDir + file, 'r')
            #print file
            for line in inFile:
                    #TODO: Perhaps some error handling here.  Issues opening file from METAR_2015-06-04-0452Z.csv
                    #print line
                    report = line.split(',')
                    key = report[0]+report[1]
                    metarDict[key] = line
            inFilesProcessed += 1
        #success deduplicating current batch now output to file
        oFile = open(rawMetarDir + "deduped/MetarDupesRemoved" + helper.getDateTimeStamp() + "-batch-"+ str(batchesComplete+1) + ".csv",'w')
        for key in sorted(metarDict):
            oFile.write(metarDict[key])

        oFile.close()
        
        #update filesInQueue by removing filesPerBatch elements
        filesInQueue = filesInQueue[filesPerBatch:]
        
        #delete files from current queue
        helper.deleteFilesInList(rawMetarDir,currentQueue)
        
        #update batch count and print message
        batchesComplete += 1
        print str(batchesComplete) + " Batches complete of " + str(totalBatches)
        
        #Done
        if len(filesInQueue) == 0:
            print "All metar files deduped"
            break      
        
#STEP 2
def batchLoadMetarReports(rawMetarDir = os.path.join(helper.getProjectPath(),'wxtalk/resources/data/metar/1-raw/deduped/')):
    '''Provided a directory path containing raw metar files.
    Function converts them to correct format for database and then loads them into database'''
    
    
    
    #Get list of deduplicated files to insert into database
    files = helper.getListOfFiles(rawMetarDir)
    files.sort()
    s = db.MetarReport()
    
    #load deduplicate files into database
    for file in files:
        start_time = time.time()
        inFile = open(rawMetarDir + file, 'r')
        inFile.readline()
        print file
        metarDictsList = []
        #convert each report to dictionary and store dictionary in list
        for line in inFile:
            metarList = line.split(",")
            try:
                metarDict = metar.getMetarDict(metarList)
                metarDictsList.append(metarDict)
            except:
                #TODO: fix error logging, currently it is logging way to much
                logger1.error('Error getMetarDict: %s',  line)
                continue
        
 
        #now load in each metar dictionary into db
        completedCount = 0
        total = len(metarDictsList)
        print "Loading " + str(total) + " metar reports into database. From file = " + file
        for dict in metarDictsList:
            #print dict
            try:
                s.loadMetarReport(dict)
            except:
                #TODO: fix error logging, currently it is logging way to much
                #print dict
                #logger1.error('Error load dict via loadMetarReport: %s',  dict)
                s = db.MetarReport()
                continue
            completedCount += 1
            if (completedCount % 1000) == 0:
                print str(completedCount) + " reports loaded of " + str(total)
        print str(completedCount) + " reports loaded of " + str(total) + " reports. From file = " + file
        print("completed in--- %s seconds ---" % (time.time() - start_time))
        
        #success so delete this file
        helper.deleteFilesInList(rawMetarDir,[file])

    

############### TWITTER/WX PIPE ####################

#STEP 1
def getTweetWxStations(tweetListofdicts,numStationsToReturn = 20,stationTable = "stations",maxStations = 3):
    '''
    Input: Tweet Dictionary,numStationsToReturn(default = 3), 
    Returns: Tweet Dictionary with 
    key = 'metar_stations' and 'climate_stations' list
    vals = [('stationID1',distanceToStationID1 in StatuteMiles),
            ('stationID2',distanceToStationID2 in StatuteMiles)]
    
    '''
    #initialise db object
    stationObj = db.Stations()
    
    returnTweetsList = []
    
    for tweetDict in tweetListofdicts:
        try:
            #get lon/lat from tweet dictionary and convert to tuple
            tweetCoordinates = tweetDict['coordinates']['coordinates']
            
            #TODO: Returns a list of metar and potentially climate stations.
            stationList = stationObj.getStationList(tweetCoordinates,maxStations = numStationsToReturn, stationTable = stationTable)
            
            climateList = []
            metarList = []
            #this is done for efficient querying, by doing this db is only queried once for both station types
            for station in stationList:
                if station[2] and (len(climateList) < maxStations):
                    climateList.append([station[0],station[1]])
                if len(metarList) < maxStations:
                    metarList.append([station[0],station[1]])
            
            #append station list to tweetDictionary
            tweetDict['metar_stations'] = metarList
            tweetDict['climate_stations'] = climateList
            
            #append updated dict to return list
            returnTweetsList.append(tweetDict)
        except:
            #dump data to error folder and continue onto next dictionary
            tweetDict['ERROR'] = 'Error occured in pipeline getTweetWxStations'
            helper.dumpJSONtoFile(os.path.join(pathToErrorDir,'pipeline-'+helper.getDateTimeStamp()+'.json'),tweetDict)
            continue
    
    #return dictionary
    return returnTweetsList


##STEP 1
#def getTweetWxStations(tweetListofdicts,numStationsToReturn = 3,desiredKeyName = 'metar_stations',stationTable = "metarStations"):
#    '''
#    Input: Tweet Dictionary,numStationsToReturn(default = 3), 
#                    desiredKeyName = 'metar_stations' or 'climate_stations' 
#                    stationTable = "metarStations" or "climateStations"
#    Returns: Tweet Dictionary with 
#    key = 'metar_stations' or 'climate_stations'
#    vals = [('stationID1',distanceToStationID1 in StatuteMiles),
#            ('stationID2',distanceToStationID2 in StatuteMiles)]
#    
#    '''
#    #initialise db object
#    stationObj = db.Stations()
#    
#    returnTweetsList = []
#    
#    for tweetDict in tweetListofdicts:
#        try:
#            #get lon/lat from tweet dictionary and convert to tuple
#            tweetCoordinates = tweetDict['coordinates']['coordinates']
#            
#            #TODO: If time permits, add in climate stations field.
#            #return list of metar stations
#            stationList = stationObj.getStationList(tweetCoordinates,maxStations = numStationsToReturn, stationTable = stationTable)
#            
#            #append station list to tweetDictionary
#            tweetDict[desiredKeyName] = stationList
#            
#            #append updated dict to return list
#            returnTweetsList.append(tweetDict)
#        except:
#            #dump data to error folder and continue onto next dictionary
#            tweetDict['ERROR'] = 'Error occured in pipeline getTweetWxStations'
#            helper.dumpJSONtoFile(os.path.join(pathToErrorDir,'pipeline-'+helper.getDateTimeStamp()+'.json'),tweetDict)
#            continue
#    
#    #return dictionary
#    return returnTweetsList



#STEP 2    
def getTweetMetarReport(tweetDict):
    '''
    Input: TweetDictionary 
    Returns: Tweet Dictionary with metar report details
    vals = {station id, dist to station, report, deltatime since report, database uid of report}
    
    Dumps the tweet to error folder if no weather report found
    
    '''
    
    #initialise db report object
    r = db.MetarReport()
    
    #set vars
    datestamp = tweetDict["created_at"]
    stationList = tweetDict["metar_stations"]
    report = []
    stationID = ''
    stationDistance = 0.0
    #we want all columns + string conversion of datetime + time delta between tweet time and wx report time
    selectString = '*, to_char(observation_time,\'YYYY-MM-DD HH24:MI:SS\'),\
                      extract(\'epoch\' from (\''+ datestamp + '\' - observation_time))' 
    
    #get wx report
    for station in stationList:
        stationID = station[0]
        stationDistance = station[1]
        tempreport = r.retrieveMetarReport(stationID,datestamp,selectString)
        #report = report[0]
        if len(tempreport) == 0:
            #No report available for stationID datestamp combo, therefore got to next station in list
            continue
        if len(tempreport) == 1:
            #we found a report
            report = tempreport[0]
            break
    
    #convert report to list
    report = list(report)
    
    #error check, raise exception and dump to file.  There was a problem with data perhaps no report found
    if report == []:
        #tweetDict['ERROR'] = 'Error occured in pipeline getTweetWxReport'
        #helper.dumpJSONtoFile(os.path.join(pathToErrorDir,'pipeline-'+helper.getDateTimeStamp()+'.json'),[tweetDict])
        raise Exception("No wx report retrieved, check data in the error folder")
    if stationID != report[0]:
        #tweetDict['ERROR'] = 'Error occured in pipeline getTweetWxReport'
        #helper.dumpJSONtoFile(os.path.join(pathToErrorDir,'pipeline-'+helper.getDateTimeStamp()+'.json'),[tweetDict])
        raise Exception("Station missmatch between retrieved report statiion = " + report[0] + "  and station ID in list provided , check data in the error folder.")

    
    #update dict by dropping list of stations and adding appropriate wx fields
    tweetDict.pop("metar_stations")
    tweetDict["metar_station_id"] = stationID
    tweetDict["metar_station_dist"] = stationDistance
    #tweetDict["metar_report"] = report[0:1] + report[-2:-1] + report[2:-3]  #returns a tuple in same format as orginal metar.  Ordered in list of db fields
    tweetDict["metar_delta_time_sec"] = report[-1]
    tweetDict["metar_db_uid"] = report[-3]
    
    return tweetDict
        
#STEP 3    
def getTweetClimateReport(tweetDict):
    '''
    Input: TweetDictionary 
    Returns: Tweet Dictionary with climate report details
    vals = {station id, dist to station, report, deltatime since report, database uid of report}
    
    '''
    
    #initialise db report object
    r = db.ClimateReport()
    
    #set vars
    datestamp = tweetDict["created_at"]
    stationList = tweetDict["climate_stations"]
    report = []
    stationID = ''
    stationDistance = 0.0
    #we want all columns + string conversion of datetime + time delta between tweet time and wx report time
    selectString = 'uid, to_char(report_start_datetime,\'YYYY-MM-DD HH24:MI:SS\'),\
                      extract(\'epoch\' from (\''+ datestamp + '\' - report_start_datetime))' 
    
    #get wx report
    for station in stationList:
        stationID = station[0]
        stationDistance = station[1]
        tempreport = r.retrieveClimateReport(stationID,datestamp,selectString)
        #report = report[0]
        if len(tempreport) == 0:
            #No report available for stationID datestamp combo, therefore got to next station in list
            continue
        if len(tempreport) == 1:
            #we found a report
            report = tempreport[0]
            break
    
    
    #convert report to list
    report = list(report)
    
    #error check, raise exception and dump to file.  There was a problem with data perhaps no report found
    #NOTE: This might be unecssary given above code
    if report == []:
        #tweetDict['ERROR'] = 'Error occured in pipeline getTweetWxReport'
        #helper.dumpJSONtoFile(os.path.join(pathToErrorDir,'pipeline-'+helper.getDateTimeStamp()+'.json'),[tweetDict])
        raise Exception("No wx report retrieved, check data in the error folder")


    #update dict by dropping list of stations and adding appropriate wx fields
    tweetDict.pop("climate_stations")
    tweetDict["climate_station_id"] = stationID
    tweetDict["climate_station_dist"] = stationDistance
    tweetDict["climate_delta_time_sec"] = report[-1]
    tweetDict["climate_db_uid"] = report[-3]
    
    return tweetDict       
    
##STEP 2    
#def getTweetWxReport(tweetDict,reportType = 'metar'):
#    '''
#    Input: TweetDictionary ,reportType = 'metar' or 'climate'
#    Returns: Tweet Dictionary with 
#    key = 'metarReport' or 'climateReport'
#    vals = {station id, dist to station, report, deltatime since report, database uid of report}
#    
#    '''
#    #TODO: Add in functionality to retrieve climate report
#    
#    #initialise db report object
#    r = db.MetarReport()
#    
#    #set vars
#    datestamp = tweetDict["created_at"]
#    stationList = tweetDict["metar_stations"]
#    report = []
#    stationID = ''
#    stationDistance = 0.0
#    #we want all columns + string conversion of datetime + time delta between tweet time and wx report time
#    selectString = '*, to_char(observation_time,\'YYYY-MM-DD HH24:MI:SS\'),\
#                      extract(\'epoch\' from (\''+ datestamp + '\' - observation_time))' 
#    
#    #get wx report
#    for station in stationList:
#        stationID = station[0]
#        stationDistance = station[1]
#        tempreport = r.retrieveMetarReport(stationID,datestamp,selectString)
#        #report = report[0]
#        if len(tempreport) == 0:
#            #No report available for stationID datestamp combo, therefore got to next station in list
#            continue
#        if len(tempreport) == 1:
#            #we found a report
#            report = tempreport[0]
#            break
#    
#    #convert report to list
#    report = list(report)
#    
#    #error check, raise exception and dump to file.  There was a problem with data perhaps no report found
#    if report == []:
#        tweetDict['ERROR'] = 'Error occured in pipeline getTweetWxReport'
#        helper.dumpJSONtoFile(os.path.join(pathToErrorDir,'pipeline-'+helper.getDateTimeStamp()+'.json'),[tweetDict])
#        raise Exception("No wx report retrieved, check data in the error folder")
#    if stationID != report[0]:
#        tweetDict['ERROR'] = 'Error occured in pipeline getTweetWxReport'
#        helper.dumpJSONtoFile(os.path.join(pathToErrorDir,'pipeline-'+helper.getDateTimeStamp()+'.json'),[tweetDict])
#        raise Exception("Station missmatch between retrieved report statiion = " + report[0] + "  and station ID in list provided , check data in the error folder.")

#    
#    #update dict by dropping list of stations and adding appropriate wx fields
#    tweetDict.pop("metar_stations")
#    tweetDict["metar_station_id"] = stationID
#    tweetDict["metar_station_dist"] = stationDistance
#    #tweetDict["metar_report"] = report[0:1] + report[-2:-1] + report[2:-3]  #returns a tuple in same format as orginal metar.  Ordered in list of db fields
#    tweetDict["metar_delta_time_sec"] = report[-1]
#    tweetDict["metar_db_uid"] = report[-3]
#    
#    return tweetDict    


