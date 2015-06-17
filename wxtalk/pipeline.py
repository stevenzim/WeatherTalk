#author: Steven Zimmerman
#created: 10-JUN-2015
#module including key processing pipeline functionality
#TODO: move stuff over from wxtalk.models.twxeety.pipeline.py

from wxtalk.wxcollector import processmetar as metar
from wxtalk import helper
from wxtalk.db import dbfuncs as db
import sys
import os
import math

import logging

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
def removeDuplicateMetar(rawMetarDir = os.path.join(helper.getProjectPath(),'wxtalk/resources/data/metar/1-raw/'),\
                        filesPerBatch = 100):
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
            print file
            for line in inFile:
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
        

def batchLoadMetarReports(rawMetarDir = os.path.join(helper.getProjectPath(),'wxtalk/resources/data/metar/1-raw/deduped/')):
    '''Provided a directory path containing raw metar files.
    Function converts them to correct format for database and then loads them into database'''
    
    #Get list of deduplicated files to insert into database
    files = helper.getListOfFiles(rawMetarDir)
    files.sort()
    s = db.MetarReport()
    
    #load deduplicate files into database
    for file in files:
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
                logger1.error('Error load dict via loadMetarReport: %s',  dict)
                s = db.MetarReport()
                continue
            completedCount += 1
            if (completedCount % 100) == 0:
                print str(completedCount) + " reports loaded of " + str(total)
        print str(completedCount) + " reports loaded of " + str(total) + " reports. From file = " + file
        
        #success so delete this file
        helper.deleteFilesInList(rawMetarDir,[file])
    

############### TWITTER/WX PIPE ####################
def getTweetWxStations(tweetListofdicts,numStationsToReturn = 3,desiredKeyName = 'metar_stations',stationTable = "metarStations"):
    '''
    Input: Tweet Dictionary,numStationsToReturn(default = 3), 
                    desiredKeyName = 'metar_stations' or 'climate_stations' 
                    stationTable = "metarStations" or "climateStations"
    Returns: Tweet Dictionary with 
    key = 'metar_stations' or 'climate_stations'
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
            
            #TODO: If time permits, add in climate stations field.
            #return list of metar stations
            stationList = stationObj.getStationList(tweetCoordinates,maxStations = numStationsToReturn, stationTable = stationTable)
            
            #append station list to tweetDictionary
            tweetDict[desiredKeyName] = stationList
            
            #append updated dict to return list
            returnTweetsList.append(tweetDict)
        except:
            #dump data to error folder and continue onto next dictionary
            tweetDict['ERROR'] = 'Error occured in pipeline getTweetWxStations'
            helper.dumpJSONtoFile(os.path.join(pathToErrorDir,'pipeline-'+helper.getDateTimeStamp()+'.json'),tweetDict)
            continue
    
    #return dictionary
    return returnTweetsList
    


