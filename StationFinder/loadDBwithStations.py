#Modified code from http://zetcode.com/db/postgresqlpythontutorial/

##NOTE you must be logged in as postgres user & be in the directory where this script is stored
#user@ubuntu-dev:~/Desktop/GitHub/WeatherTalk/WeatherScripts$ sudo su - postgres
#postgres@ubuntu-dev:~$ cd /home/user/Desktop/GitHub/WeatherTalk/WeatherScripts



'''THIS IS A BRUTE FORCE WAY TO LOAD THE MASTER STATION LIST INTO DATABASE'''

import psycopg2
import sys


#open database connection
connection = psycopg2.connect("dbname=weather user=postgres password=postgres") 
cursor = connection.cursor()

#drop existing table
cursor.execute("DROP TABLE stations;")
connection.commit()

#create table
addTableCmd = "CREATE TABLE stations (ICAO_ID CHAR(4), latitude float, longitude float, location point, name VARCHAR(50));"
cursor.execute(addTableCmd)
connection.commit()

#load stations from master station list
iFile = open('ClimMasterStationList.csv','r')
iFile.readline()
masterListCommands = []
for line in iFile:
	stationItems = line.split(',')
	#point is (Longitude, Latitude) to match same order as tweets
	point = "(" + stationItems[6] + "," + stationItems[5] + ")"
	dbPreStr = 'INSERT INTO stations (ICAO_ID, latitude, longitude,location, name) VALUES('
	stationString = '\'' + stationItems[4] + '\',' + stationItems[5] + ',' + stationItems[6] + ',POINT' + point + ',\'' + stationItems[2] + '\''
	dbPostStr = ');'
	dbCommandStr = dbPreStr + stationString + dbPostStr
	masterListCommands.append(dbCommandStr)




#write stations and points to db
for sqlCommand in masterListCommands:
	cursor.execute(sqlCommand)
	connection.commit()

connection.close()	















# try:
     
    # connection = psycopg2.connect("dbname=weather user=postgres") 
    # cursor = connection.cursor()
		
		# for sqlCommands in masterListCommands:
			# cursor.execute(sqlCommands)
		
		
    # cursor.execute('SELECT version()')          
    # version = cursor.fetchone()
    # print version

    # #INSERT INTO stations (ICAO_ID, latitude, longitude, name) VALUES('KATY', 44.9, -97.15, 'Watertown Regional Airport');
    

# except psycopg2.DatabaseError, e:
    # print 'Error %s' % e    
    # sys.exit(1)
    
    
# finally:
    
    # if connection:
        # connection.close()
