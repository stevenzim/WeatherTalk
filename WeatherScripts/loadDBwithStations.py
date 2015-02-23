#Modified code from http://zetcode.com/db/postgresqlpythontutorial/

##NOTE you must be logged in as postgres user & be in the directory where this script is stored
#user@ubuntu-dev:~/Desktop/GitHub/WeatherTalk/WeatherScripts$ sudo su - postgres
#postgres@ubuntu-dev:~$ cd /home/user/Desktop/GitHub/WeatherTalk/WeatherScripts

'''THIS IS A BRUTE FORCE WAY TO LOAD THE MASTER STATION LIST INTO DATABASE'''

import psycopg2
import sys

connection = None


iFile = open('MasterStationList.txt','r')
iFile.readline()
masterListCommands = []
for line in iFile:
	stationItems = line.split(',')
	dbPreStr = 'INSERT INTO stations (ICAO_ID, latitude, longitude, name) VALUES('
	stationString = '\'' + stationItems[4] + '\',' + stationItems[5] + ',' + stationItems[6] + ',\'' + stationItems[2] + '\''
	dbPostStr = ');'
	dbCommandStr = dbPreStr + stationString + dbPostStr
	masterListCommands.append(dbCommandStr)


connection = psycopg2.connect("dbname=weather user=postgres") 
cursor = connection.cursor()


for sqlCommands in masterListCommands:
	cursor.execute(sqlCommands)

connection.close()	

#cursor.execute("SELECT * FROM stations WHERE ICAO_ID = 'KSEA';")













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