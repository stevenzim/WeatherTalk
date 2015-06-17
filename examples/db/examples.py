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



#example to find nearest reports
c = db.Connector()
sqlstring = 'SELECT * FROM weather.metar_report\
            WHERE ICAO_ID = \'KSEA\''
c.cursor.execute(sqlstring)
reports = c.cursor.fetchall()


#example to retrieve latest metar report
c = db.Connector()
sqlstring = 'SELECT *\
            FROM weather.metar_report\
            WHERE ICAO_ID = \'KSEA\'  AND observation_time <= \'Sat May 23 20:59:30 +0000 2015\'::timestamp\
            ORDER BY observation_time DESC LIMIT 1;'
c.cursor.execute(sqlstring)
reports = c.cursor.fetchall()

#playbox          
sqlstring = 'SELECT *\
            FROM weather.metar_report\
            WHERE ICAO_ID = \'KSEA\'  AND observation_time <= \'2015-05-23 14:58:49\'::timestamp\
            ORDER BY observation_time DESC LIMIT 1;'
            
reports = c.cursor.fetchall()

#crap
sqlstring = 'SELECT observation_time\
             FROM weather.metar_report\
             WHERE weather.observation_time <= timestamp \'Sat May 23 20:59:30 +0000 2015\''        

sqlstring = '\'Sat May 23 20:59:30 +0000 2015\'::timestamp'
sqlstring = '\'2013-08-20 14:52:49\'::timestamp'

sqlstring = 'SELECT * FROM weather.metar_report\
            WHERE observation_time >= (\'2015-05-23 14:52:49\'::timestamp - \'1 hours\'::timestamp) AND ICAO_ID = \'KSEA\';'

#from http://dba.stackexchange.com/questions/27823/query-to-find-closest-lesser-date
SELECT 
    a.WorkCenter
  , a.ActionDate
  , a.Hours
  , r.Rate
  , r.Rate * a.Hours  AS Cost
FROM 
    Activities AS a
  JOIN
    Rates AS r
      ON  r.StartDate = 
          ( SELECT MAX(StartDate)
             FROM Rates 
             WHERE StartDate <= a.ActionDate
          ) ;
