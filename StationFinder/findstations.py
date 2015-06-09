import psycopg2
import sys


#TODO: Create tests

class Stations(object):
    '''
    usage:
    import findstations
    db = findstations.Stations()
    db.getStationList([-75.,44.])
    
    returns [('KSLK', 48.312), ('KMSS', 64.681), ('KART', 51.219)]
    '''
    def __init__(self):
        self.connection = psycopg2.connect("dbname=weather user=postgres password=postgres") 
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
        FROM stations \
        ORDER BY round((location <@> point" + stationCoordString + ")::numeric, 3) \
        limit " + str(maxStations) + ";" 
        
        
        listToReturn = []
        self.cursor.execute(sql)
        listOfStations = self.cursor.fetchall()
        for record in listOfStations:
            stationID = record[0]
            stationDistance = record[-1].__float__()
            listToReturn.append((stationID,stationDistance))
        
        return listToReturn    



