import os
import mysql.connector
from collectors import helper
from collectors.metar import processMETAR
from collectors.metar import dbMETAR

rawDataPath = 'data/METAR/raw/'      #path to raw data files
procDataPath = 'data/METAR/processed/'      #path to processed data files
errorPath = 'data/METAR/error.csv'

#db connection
cnx = mysql.connector.connect(user='python', password='python',
                              host='127.0.0.1', db='weather')
cursor = cnx.cursor()

#error logging file
errFile = open(errorPath,'a')

listRawFiles = helper.getListOfFiles(rawDataPath)
for file in listRawFiles:
    filePath = rawDataPath + file
    iFile = open(filePath,'r')
    iFile.readline() #header
    for line in iFile:
        metarList = line.split(',')
        try:
            metarDict = processMETAR.getMetarDict(metarList)
            cursor.execute(dbMETAR.add_metar,metarDict)
        except:
            errFile.write(line)
            print line

errFile.close()


cursor.execute("SELECT concat_station_date FROM METAR WHERE concat_station_date='KPHL2015-03-31T23:59:00Z'")
rows = cursor.fetchall()
for row in rows:
    print row