#Author: Steven Zimmerman
#Date: 16-JUN-2015

#Modified code from http://zetcode.com/db/postgresqlpythontutorial/

##NOTE you must be logged in as postgres user & be in the directory where this script is stored
#user@ubuntu-dev:~/Desktop/GitHub/WeatherTalk/WeatherScripts$ sudo su - postgres
#postgres@ubuntu-dev:~$ cd /home/user/Desktop/GitHub/WeatherTalk/WeatherScripts

import psycopg2
import sys

#open database connection
connection = psycopg2.connect("dbname=weather user=steven password=steven") 
cursor = connection.cursor()

#drop existing table
cursor.execute("DROP TABLE weather.metar_report;")
connection.commit()


#open database connection
connection = psycopg2.connect("dbname=weather user=steven password=steven") 
cursor = connection.cursor()

#create table
addTableCmd = "CREATE TABLE weather.metar_report \
(\
ICAO_ID CHAR(4),\
observation_time timestamp,\
temp_c float,\
dewpoint_c float,\
wind_dir_degrees smallint,\
wind_speed_kt smallint,\
wind_gust_kt smallint,\
visibility_statute_mi float,\
altim_in_hg float,\
corrected bool,\
maintenance_indicator_on bool,\
wx_string char(20),\
precip_rain smallint,\
precip_snow smallint,\
precip_drizzle smallint,\
precip_unknown smallint,\
thunderstorm bool,\
hail_graupel_pellets bool,\
fog_mist bool,\
transmissivity_clouds float,\
max_cloud_cov float,\
metar_type char(10),\
remark text,\
PRIMARY KEY (ICAO_ID, observation_time),\
CONSTRAINT metar_report_station_id_fkey FOREIGN KEY (ICAO_ID)\
  REFERENCES weather.metarStations (ICAO_ID) MATCH SIMPLE\
  ON UPDATE NO ACTION ON DELETE NO ACTION\
);"
cursor.execute(addTableCmd)
connection.commit()



###Example to load in data into db
from wxtalk.wxcollector import processmetar as metar

metarRep1 = 'KNCA,2015-05-22T14:05:00Z,17.2,11.1,360,9,,10.0,30.15059,,,,BKN,3000,,,,,,,SPECI, AO2 T01720111'
metarList1 = metarRep1.split(",")
metarDict1 = metar.getMetarDict(metarList1)


#inspired by http://stackoverflow.com/questions/29461933/insert-python-dictionary-using-psycopg2
#convert keys to column names and then create string
columns = metarDict1.keys()
columns_str = ", ".join(columns)
#convert values to column names and then create string
values = [metarDict1[x] for x in columns]
values_str_list = [str(value) for value in values]
values_str = "\',\'".join(values_str_list)
#create insert string
sqlstring = 'INSERT INTO weather.metar_report (' + columns_str + ')\
                         VALUES (\'' + values_str + '\');'
                                            
#insert metar report into table
cursor.execute(sqlstring)
connection.commit()

                         
#retrieve records from db
cursor.execute('select * from weather.metar_report')
cursor.fetchall()

#delete metar report from table example
sqlstring = 'DELETE FROM weather.metar_report\
            WHERE ICAO_ID = \'KNCA\' AND observation_time = \'2015-05-22T14:05:00\''
cursor.execute(sqlstring)
connection.commit()


#load stations from master station list
iFile = open(stationCsvFilePath,'r')
iFile.readline()
masterListCommands = []
for line in iFile:
    stationItems = line.split(',')
    #point is (Longitude, Latitude) to match same order as tweets
    point = "(" + stationItems[6] + "," + stationItems[5] + ")"
    dbPreStr = 'INSERT INTO weather.' + tableName + '(ICAO_ID, latitude, longitude,location, name) VALUES('
    stationString = '\'' + stationItems[4] + '\',' + stationItems[5] + ',' + stationItems[6] + ',POINT' + point + ',\'' + stationItems[2] + '\''
    dbPostStr = ');'
    dbCommandStr = dbPreStr + stationString + dbPostStr
    masterListCommands.append(dbCommandStr)




#write stations and points to db
for sqlCommand in masterListCommands:
    cursor.execute(sqlCommand)
    connection.commit()

connection.close()	
print "Data loaded to " + tableName + " table with data from " + stationCsvFilePath + " successfully."















