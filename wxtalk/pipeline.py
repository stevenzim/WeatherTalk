#author: Steven Zimmerman
#created: 10-JUN-2015
#module including key processing pipeline functionality
#TODO: move stuff over from wxtalk.models.twxeety.pipeline.py

from wxtalk import helper
from wxtalk.db import findstations as fs
import sys


def getTweetWxStations(tweetListofdicts,numStationsToReturn = 3):
    '''
    Input: Tweet Dictionary,numStationsToReturn(default = 3)
    Returns: Tweet Dictionary with 
    key = 'metar_stations' 
    vals = [('stationID1',distanceToStationID1 in StatuteMiles),
            ('stationID2',distanceToStationID2 in StatuteMiles)]
    
    '''
    #initialise db object
    stationObj = fs.Stations()
    
    returnTweetsList = []
    
    for tweetDict in tweetListofdicts:
        try:
            #get lon/lat from tweet dictionary and convert to tuple
            tweetCoordinates = tweetDict['coordinates']['coordinates']
            
            #TODO: If time permits, add in climate stations field.
            #return list of metar stations
            stationList = stationObj.getStationList(tweetCoordinates)
            
            #append station list to tweetDictionary
            tweetDict['metar_stations'] = stationList
            
            #append updated dict to return list
            returnTweetsList.append(tweetDict)
        except:
            #TODO: Decide if I want to dump the data somewhere??
            tweetDict['ERROR'] = 'Error occured in pipeline getTweetWxStations'
            helper.dumpJSONtoFile('../errors/pipeline-'+helper.getDateTimeStamp()+'.json',tweetDict)
            continue
    
    #return dictionary
    return returnTweetsList
    


