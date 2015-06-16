from wxtalk.wxcollector import processmetar as metar
from wxtalk.db import dbfuncs as db
from wxtalk import helper

###simple Example to load in data into db
metarRep = 'KNCA,2000-01-01T00:00:00Z,0,0,0,0,,0,30.15059,,,,,,,,,,,,,'
metarList = metarRep.split(",")
metarDict = metar.getMetarDict(metarList)

s = db.MetarReport()
s.loadMetarReport(metarDict)

#example to fetch data
c = db.Connector()
sqlstring = 'SELECT * FROM weather.metar_report\
            WHERE ICAO_ID = \'' + metarDict['ICAO_ID'] + '\' AND observation_time = \'' + metarDict['observation_time'] + '\''
c.cursor.execute(sqlstring)
reports = c.cursor.fetchall()


#example to load in a set of metar reports and files
#clean up metar
#remove dupes
#dump to new csv file
#a prototype to quickly get rid of duplicate metars
files = helper.getListOfFiles("data/")
files.sort()
s = db.MetarReport()

for file in files:
    inFile = open("data/" + file, 'r')
    inFile.readline()
    print file
    metarDictsList = []
    #convert each report to dictionary and store in list
    for line in inFile:
        metarList = line.split(",")
        try:
            metarDict = metar.getMetarDict(metarList)
            metarDictsList.append(metarDict)
        except:
            print line
            continue
        
    #now load in dictionary
    counter = 0
    total = len(metarDictsList)
    for dict in metarDictsList:
        try:
            s.loadMetarReport(dict)
        except:
            print dict
            s = db.MetarReport()
            continue
        counter += 1
        print str(counter) + " reports loaded of " + str(total) + " reports. From file = " + file


metarDict = {}
for file in files:
    inFile = open("consec/" + file, 'r')
    print file
    for line in inFile:
            report = line.split(',')
            key = report[0]+report[1]
            metarDict[key] = line

oFile = open("MetarDupesRemoved.csv",'w')
for key in metarDict:
    oFile.write(metarDict[key])

oFile.close()
