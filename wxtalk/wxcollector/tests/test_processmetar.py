from nose.tools import *
import os
from wxtalk.wxcollector import processmetar as metar

#maxCloudCover test data in ["inputstring",expectedResults]
test1 = ["CLR,,,,,,,",0.0]
test2 = [",,,,,,,",-999.0]
test3 = ["SCT,1100,BKN,4000,OVC,4900,,",1.0]
test4 = ["SCT,1100,BKN,4000,FEW,4900,FEW,5200",.75]
test5 = ["SCT,1800,FEW,4900,,,,",.4375]
test6 = ["FEW,1000,,,,,,",.1875]
test7 = ["OVX,,,,,,,",1.0]
test8 = ["SKC,,,,,,,",0.0]


#precip test data
wxstring1 = '+TSRA FG SQ'  #heavy rain, tstorm, fog, squall
wxstring2 = '-TSRA FC GR' #light rain, tstorm, tornado, hail
wxstring3 = 'DZ GS' #moderate drizzle


def test_set_max_cloud_cover():
    '''Test to verify correct max sky cover value is returned.'''
    assert_equal(metar.setMaxCloudCover(test1[0].split(",")),test1[1])
    assert_equal(metar.setMaxCloudCover(test2[0].split(",")),test2[1])    
    assert_equal(metar.setMaxCloudCover(test3[0].split(",")),test3[1])
    assert_equal(metar.setMaxCloudCover(test4[0].split(",")),test4[1])
    assert_equal(metar.setMaxCloudCover(test5[0].split(",")),test5[1])    
    assert_equal(metar.setMaxCloudCover(test6[0].split(",")),test6[1])
    assert_equal(metar.setMaxCloudCover(test7[0].split(",")),test7[1])
    assert_equal(metar.setMaxCloudCover(test8[0].split(",")),test8[1])    
    
    
def test_precip_values():
    '''Test to verify correct precip intensity is returned.'''
    assert_equal(metar.setPrecipVals(wxstring1,'SN'),0)
    assert_equal(metar.setPrecipVals(wxstring1,'RA'),3)
    assert_equal(metar.setPrecipVals(wxstring2,'RA'),1)
    assert_equal(metar.setPrecipVals(wxstring3,'DZ'),2)
    assert_equal(metar.setPrecipVals("",'DZ'),0)

def test_wx_type_boolean():
    '''Test to verify correct boolean value returned based on list of wx values to test for.'''
    assert_equal(metar.setWxTypeBoolean(wxstring1,['TS']),True)
    assert_equal(metar.setWxTypeBoolean(wxstring1,['GR','GS']),False)
    assert_equal(metar.setWxTypeBoolean(wxstring1,['FG','BR']),True)
    assert_equal(metar.setWxTypeBoolean(wxstring3,['TS']),False)
    assert_equal(metar.setWxTypeBoolean(wxstring3,['GR','GS']),True)
    assert_equal(metar.setWxTypeBoolean(wxstring3,['FG','BR']),False)

