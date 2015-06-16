from nose.tools import *
from wxtalk.db import dbfuncs as db



def test_getstationlist():
    '''
    Given longitude,latitude optional total number of stations, 
    returns a list of stations and distances
    '''
    dbObj = db.Stations()
    #basic test
    #climate table
    assert_equal(dbObj.getStationList([-75.,44.],stationTable = "climateStations"),\
                    [['KSLK', 48.312], ['KART', 51.219], ['KMSS', 64.681]])
    #cliamte table with one record returned
    assert_equal(dbObj.getStationList([-75.,44.],1,stationTable = "climateStations"),\
                    [['KSLK', 48.312]])
                    
    #metar field
    assert_equal(dbObj.getStationList([-75.,44.]),\
                    [['KGTB', 36.089], ['KSLK', 48.312], ['KART', 51.219]])               
                    
    #exception tests
    assert_raises(TypeError,\
            dbObj.getStationList,[] ) #test1 error thrown when list not passed
    assert_raises(TypeError,\
        dbObj.getStationList,"HELLO" ) #test2 error thrown when list not passed
    # verification that cursor was closed and reset properly after exception
    assert_equal(dbObj.getStationList([-75.,44.],1,stationTable = "climateStations"),\
                    [['KSLK', 48.312]])
                    
#TODO: Create test for loading metar reports.  Currently only have examples that show this works
####Example to load in data into db
#from wxtalk.wxcollector import processmetar as metar
#from wxtalk.db import dbfuncs as db
#metarRep = 'KNCA,2000-01-01T00:00:00Z,0,0,0,0,,0,30.15059,,,,,,,,,,,,,'
#metarList = metarRep.split(",")
#metarDict = metar.getMetarDict(metarList)

#s = db.MetarReport()
#s.loadMetarReport(metarDict1)

##example to fetch data
#c = db.Connector()
#sqlstring = 'SELECT * FROM weather.metar_report\
#            WHERE ICAO_ID = \'' + metarDict['ICAO_ID'] + '\' AND observation_time = \'' + metarDict['observation_time'] + '\''
#c.cursor.execute(sqlstring)
#reports = c.cursor.fetchall()
