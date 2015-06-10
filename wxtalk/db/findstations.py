#author: Steven Zimmerman
#created: 09-JUN-2015
#module to retrieve wx station information from weather db

import psycopg2
import sys

class Stations(object):
    '''
    usage:
    from db import findstations
    db = findstations.Stations()
    db.getStationList([-75.,44.])
    
    returns [('KSLK', 48.312), ('KMSS', 64.681), ('KART', 51.219)]
    '''
    def __init__(self,connectionParams = "dbname=weather user=steven password=steven"):
        #TODO: If time permits, clean this up so user and pw are passed in
        self.conparams = connectionParams
        self.connection = psycopg2.connect(self.conparams) 
        self.cursor = self.connection.cursor()

    def getStationList(self,twitterCoords,maxStations = 3):
        '''
        Pass in a list of coordinates in [longitude,latitude] format
        Returns a list of tuples containing top 3 
        '''
        stationCoordString = str(tuple(twitterCoords))

        #sql statement to retrieve sorted list of stations with distances in statue miles
        sql = "SELECT ICAO_ID, name, latitude, longitude, location,\
               round((location <@> point" + stationCoordString + ")::numeric, 3) as miles \
        FROM weather.stations \
        ORDER BY round((location <@> point" + stationCoordString + ")::numeric, 3) \
        limit " + str(maxStations) + ";" 
        
        
        listToReturn = []
        
        #error handling in the event that wrong point format thrown in
        try:
            self.cursor.execute(sql)
            listOfStations = self.cursor.fetchall()
        except:
            #restablish connection and throw exception error
            #TODO: Consider if there is a better way to restablish the connection
            self.cursor.close()
            self.connection = psycopg2.connect(self.conparams) 
            self.cursor = self.connection.cursor()
            raise TypeError("Coordinate must be passed in as list/tuple format (lat,lon)")

        for record in listOfStations:
            stationID = record[0]
            stationDistance = record[-1].__float__()
            listToReturn.append([stationID,stationDistance])
        
        return listToReturn    



