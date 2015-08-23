#Inspired by code from http://zetcode.com/db/postgresqlpythontutorial/
'''A BRUTE FORCE WAY TO LOAD THE MASTER STATION LIST INTO DATABASE'''

import psycopg2
import sys
from wxtalk.db import dbfuncs as db
from wxtalk import helper


addTableCmd = "CREATE TABLE weather.stations\
    (\
      icao_id character(4) PRIMARY KEY,\
      latitude double precision,\
      longitude double precision,\
      lat_lon_point point,\
      climate_station boolean,\
      nearest_climate_icao_id character(4),\
      nearest_climate_dist_sm float,\
      city varchar(100),\
      state varchar(20),\
      utc_offset smallint,\
      daily_report_start_time_utc varchar(50) ,\
      daily_report_end_time_utc varchar(50));"

def createStationTable(csvFilePath):
    #open database connection
    d = db.Connector()

    try:
        #drop existing table
        d.cursor.execute("DROP TABLE weather.stations;")
        d.connection.commit()
        #create table
        d.cursor.execute(addTableCmd)
        d.connection.commit()
    except:
        d = db.Connector()
        #create table
        d.cursor.execute(addTableCmd)
        d.connection.commit()
    
    #get dicts of stations to load
    listOfStations = helper.csvToDicts(csvFilePath)
    
    #load stations
    for dict in listOfStations:
    #create insert string
        columns_str, values_str = helper.keysValsToSQL(dict)
        sqlinsertstring = 'INSERT INTO weather.stations (' + columns_str + ')\
                                 VALUES (\'' + values_str + '\');'
        #write station to db
        d.cursor.execute(sqlinsertstring)
        d.connection.commit()

    d.connection.close()	
    print "Stations loaded to station table successfully."










