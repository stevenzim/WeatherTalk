import psycopg2
import sys

def getStationList(twitterCoords,maxStations = 3):
    '''
    Pass in a list of coordinates in [longitude,latitude] format
    Returns a list of tuples containing top 3 
    '''
    connection = psycopg2.connect("dbname=weather user=postgres password=postgres") 
    cursor = connection.cursor()

    stationCoordString = str(tuple(twitterCoords))

    sql = "SELECT ICAO_ID, name, latitude, longitude, location,\
           round((location <@> point" + stationCoordString + ")::numeric, 3) as miles \
    FROM stations \
    ORDER BY location <-> point" + stationCoordString + " \
    limit " + str(maxStations) + ";"
    
    listToReturn = []
    cursor.execute(sql)
    listOfStations = cursor.fetchall()
    for record in listOfStations:
        stationID = record[0]
        stationDistance = record[-1].__float__()
        listToReturn.append((stationID,stationDistance))
    
    
    connection.close()
    
    return listToReturn
        




