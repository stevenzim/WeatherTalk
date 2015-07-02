from wxtalk.wxcollector import processmetar as metar
from wxtalk.db import dbfuncs as db
from wxtalk import helper
import time

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

d = db.Connector()
metarDict ={'icao_id':'K0F2'}
sqlstring = 'SELECT * FROM weather.metar\
            WHERE icao_id = \'' + metarDict['icao_id'] + '\''
d.cursor.execute(sqlstring)
reports = c.cursor.fetchall()


#example to find nearest reports for a station
c = db.Connector()
sqlstring = 'SELECT * FROM weather.metar_report\
            WHERE ICAO_ID = \'KSEA\''
c.cursor.execute(sqlstring)
reports = c.cursor.fetchall()


#example to retrieve latest metar report relative to station and time provided most recent report first
r = db.MetarReport()
r.retrieveMetarReport('KSEA',helper.getDateTimeStamp(ansiFormat = True)) #returns all fields for most recent report
r.retrieveMetarReport('KSEA','Sat May 23 20:59:30 +0000 2015') #returns all fields for most recent report relative to input time
r.retrieveMetarReport('KJFK','Sat May 23 20:59:30 +0000 2015','uid') #returns only the uid field
r.retrieveMetarReport('KSEA',helper.getDateTimeStamp(ansiFormat = True), 'observation_time, temp_c','100') #returns temperature in celsius for last 100 reports from Seattle
r.retrieveMetarReport('KSEA',helper.getDateTimeStamp(ansiFormat = True), 'to_char(observation_time,\'YYYY-MM-DD HH24:MI:SS\'), temp_c','100') # returns with datetime in readable format
r.retrieveMetarReport('KSEA',helper.getDateTimeStamp(ansiFormat = True), '*, to_char(observation_time,\'YYYY-MM-DD HH24:MI:SS\')','100') #returns all with formatted date at end
r.retrieveMetarReport('KSEA',\
                      'Sat May 23 20:59:30 +0000 2015',\
                      'to_char(observation_time,\'YYYY-MM-DD HH24:MI:SS\'),\
                      extract(\'epoch\' from (\'Sat May 23 20:59:30 +0000 2015\' - observation_time)),\
                       temp_c')      #returns nearest observation time, seconds since observation, temperature in celsius                

stime = time.time()
r.retrieveMetarReport('KSEA','Sat May 23 20:59:30 +0000 2015', 'to_char(observation_time,\'YYYY-MM-DD HH24:MI:SS\'), temp_c','100')
print ("completed in--- %s seconds ---" % (time.time() - stime))


#example to retrieve latest climatereport relative to station and time provided most recent report first
r = db.ClimateReport()
r.retrieveClimateReport('KSEA',helper.getDateTimeStamp(ansiFormat = True)) #returns all fields for most recent report
r.retrieveClimateReport('KSEA','Sat May 23 20:59:30 +0000 2015') #returns all fields for report with starttime within 24 hours of tweet
r.retrieveClimaterReport('KJFK','Sat May 23 20:59:30 +0000 2015','uid') #returns only the uid field

#example to retrieve count of tweets where temp > 15
select id from weather.tweet where sentiment_score = 1
uid
metar_db_uid
SELECT
	tweet.metar_db_uid,
	metar.uid,
	B.pkb,
	B.c2
FROM
	A
INNER JOIN B ON A .pka = B.fka;
SELECT
	A.pka,
	A.c1,
	B.pkb,
	B.c2
FROM
	A
INNER JOIN B ON A .pka = B.fka;
