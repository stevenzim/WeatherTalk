#author: Steven Zimmerman
#created: 10-JUN-2015
#module including key processing pipeline functionality
#TODO: move stuff over from wxtalk.models.twxeety.pipeline.py

from wxtalk import helper
from wxtalk.db import dbfuncs as db
import sys
import os

pathToErrorDir = os.path.join(helper.getProjectPath(),'wxtalk/errors/')


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
    


