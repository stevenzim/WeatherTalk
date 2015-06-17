from nose.tools import *
from wxtalk import pipeline
from wxtalk import helper

import os

projPathToData = os.path.join(helper.getProjectPath(),'wxtalk/tests/test-data/')

test1in = helper.loadJSONfromFile(os.path.join(projPathToData,'stationTest1-in.json'))  #post classification tweets
test1expect = helper.loadJSONfromFile(os.path.join(projPathToData,'stationTest1-expect.json'))  #post classification tweets

test2in = helper.loadJSONfromFile(os.path.join(projPathToData,'stationTest2-in.json'))  #post classification tweets
test2expect = helper.loadJSONfromFile(os.path.join(projPathToData,'stationTest2-expect.json'))  #post classification tweets

#os.path.join(user_paths,projPathToData)

#tempFile = 'test-data/temp.json'

#test1in = helper.loadJSONfromFile('test-data/stationTest1-in.json')  #post classification tweets
#test1expect = helper.loadJSONfromFile('test-data/stationTest1-expect.json')  #post classification tweets

#test2in = helper.loadJSONfromFile('test-data/stationTest2-in.json')  #post classification tweets
#test2expect = helper.loadJSONfromFile('test-data/stationTest2-expect.json')  #post classification tweets

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

