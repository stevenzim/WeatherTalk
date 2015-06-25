#Modified code from http://zetcode.com/db/postgresqlpythontutorial/

##NOTE you must be logged in as postgres user & be in the directory where this script is stored
#user@ubuntu-dev:~/Desktop/GitHub/WeatherTalk/WeatherScripts$ sudo su - postgres
#postgres@ubuntu-dev:~$ cd /home/user/Desktop/GitHub/WeatherTalk/WeatherScripts



'''THIS IS A BRUTE FORCE WAY TO LOAD THE MASTER STATION LIST INTO DATABASE'''

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

    #drop existing table
    d.cursor.execute("DROP TABLE weather.stations;")
    d.connection.commit()

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

#def createStationTable(tableName,stationCsvFilePath):
#    #open database connection
#    connection = psycopg2.connect("dbname=weather user=steven password=steven") 
#    cursor = connection.cursor()

#    #drop existing table
#    cursor.execute("DROP TABLE weather." + tableName + ";")
#    connection.commit()

#    #create table
#    addTableCmd = "CREATE TABLE weather." + tableName + " (ICAO_ID CHAR(4) PRIMARY KEY, latitude float, longitude float, location point, name VARCHAR(50));"
#    cursor.execute(addTableCmd)
#    connection.commit()

#    #load stations from master station list
#    iFile = open(stationCsvFilePath,'r')
#    iFile.readline()
#    masterListCommands = []
#    for line in iFile:
#	    stationItems = line.split(',')
#	    #point is (Longitude, Latitude) to match same order as tweets
#	    point = "(" + stationItems[6] + "," + stationItems[5] + ")"
#	    dbPreStr = 'INSERT INTO weather.' + tableName + '(ICAO_ID, latitude, longitude,location, name) VALUES('
#	    stationString = '\'' + stationItems[4] + '\',' + stationItems[5] + ',' + stationItems[6] + ',POINT' + point + ',\'' + stationItems[2] + '\''
#	    dbPostStr = ');'
#	    dbCommandStr = dbPreStr + stationString + dbPostStr
#	    masterListCommands.append(dbCommandStr)




#    #write stations and points to db
#    for sqlCommand in masterListCommands:
#	    cursor.execute(sqlCommand)
#	    connection.commit()

#    connection.close()	
#    print "Data loaded to " + tableName + " table with data from " + stationCsvFilePath + " successfully."


##create Climate Station Table
#createStationTable("climateStations",'../resources/db/ClimMasterStationList.csv')

##create METAR Station Table
#createStationTable("metarStations",'../resources/db/MetarMasterList.csv')


#Indexes
#'CREATE INDEX metar_station_loc_idx ON weather.metarStations USING gist(location);'








