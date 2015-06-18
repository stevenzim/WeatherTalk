from nose.tools import *
from wxtalk import pipeline
from wxtalk import helper

import os

projPathToData = os.path.join(helper.getProjectPath(),'wxtalk/tests/test-data/')

test1in = helper.loadJSONfromFile(os.path.join(projPathToData,'stationTest1-in.json'))  #tweets with coordinates only
test1expect = helper.loadJSONfromFile(os.path.join(projPathToData,'stationTest1-expect.json'))  #tweets with station list

test2in = helper.loadJSONfromFile(os.path.join(projPathToData,'stationTest2-in.json')) #tweets with coordinates only
test2expect = helper.loadJSONfromFile(os.path.join(projPathToData,'stationTest2-expect.json'))  #tweets with station list




def test_get_tweet_wxstations():
    '''
    Given a dictionary of live tweets.  Should return live tweet dictionary with added wx stations field
    with list of wx stations and distance to wx station
    '''
    #basic test to get stations for list of dicts
    test = pipeline.getTweetWxStations(test1in,stationTable = "climateStations")
    assert_equal(test,test1expect)
    
    #test to ensure tweet with bad data is dropped from list
    test = pipeline.getTweetWxStations(test2in,stationTable = "climateStations")
    assert_equal(test,test2expect)



#NOTE: These two fake metar reports must be loaded into db for tests to work
#from wxtalk.wxcollector import processmetar as metar
#from wxtalk.db import dbfuncs as db
#metarRep1 = 'KNCA,2000-01-01T00:00:00Z,0,0,0,0,,0,30.15059,,,,,,,,,,,,,'
#metarRep2 = 'KMOT,2000-01-01T00:00:00Z,0,0,0,0,,0,30.15059,,,,,,,,,,,,,'
#metarList = metarRep.split(",")
#metarDict = metar.getMetarDict(metarList)
#s = db.MetarReport()
#s.loadMetarReport(metarDict)

tweetWxtest1in = helper.loadJSONfromFile(os.path.join(projPathToData,'tweetWxLinkTest1-in.json'))  #tweets with station list
tweetWxtest1expect = helper.loadJSONfromFile(os.path.join(projPathToData,'tweetWxLinkTest1-expect.json'))  #tweets with metar report
tweetWxtest2in = helper.loadJSONfromFile(os.path.join(projPathToData,'tweetWxLinkTest2-in.json'))  #tweets with station list
tweetWxtest2expect = helper.loadJSONfromFile(os.path.join(projPathToData,'tweetWxLinkTest2-expect.json'))  #tweets with metar report


def test_output_tweet_json_with_wx():
    '''
    Given a list of dictionaries of live tweets with wx stations list, should return a list of dictionaries with wx reports included.  
    as well as other specified key/vals
    '''
    #test to get wx station for nearest station for list of dicts
    test = pipeline.getTweetWxReport(tweetWxtest1in[0])
    helper.dumpJSONtoFile(os.path.join(projPathToData,'temp.json'),test)
    test = helper.loadJSONfromFile(os.path.join(projPathToData,'temp.json'))
    assert_equal(test,tweetWxtest1expect[0])
    
    #test to get wx station for next nearest station.  e.g. when nearest station does not have a report available
    test = pipeline.getTweetWxReport(tweetWxtest2in[0])
    helper.dumpJSONtoFile(os.path.join(projPathToData,'temp.json'),test)
    test = helper.loadJSONfromFile(os.path.join(projPathToData,'temp.json'))
    assert_equal(test,tweetWxtest2expect[0])
 
