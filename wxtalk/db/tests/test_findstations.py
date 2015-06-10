from nose.tools import *
from wxtalk.db import findstations as fs



def test_getstationlist():
    '''
    Given longitude,latitude optional total number of stations, 
    returns a list of stations and distances
    '''
    fsObj = fs.Stations()
    #basic test
    assert_equal(fsObj.getStationList([-75.,44.]),\
                    [['KSLK', 48.312], ['KART', 51.219], ['KMSS', 64.681]])
    assert_equal(fsObj.getStationList([-75.,44.],1),\
                    [['KSLK', 48.312]])
                    
    #exception tests
    assert_raises(TypeError,\
            fsObj.getStationList,[] ) #test1 error thrown when list not passed
    assert_raises(TypeError,\
        fsObj.getStationList,"HELLO" ) #test2 error thrown when list not passed
    # verification that cursor was closed and reset properly after exception
    assert_equal(fsObj.getStationList([-75.,44.],1),\
                    [['KSLK', 48.312]])
