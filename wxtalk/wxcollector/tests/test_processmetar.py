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


#remark test data
remark1 = 'AO2A CB DSNT NE MOV E SLP208 P0000 60000 T00960056 10124 20096 57010' #precip last hour = 0 or trace, pressure tendency = decreased 1.0 hPa in past 3 hours
remark2 = 'AO2A  P0105 52043 TORNADO' #precip last hour = 1.05 , pressure tendency = increased 4.3 hPa in past 3 hours, tornado true
remark3 = 'AO2A 50000 FUNNEL CLOUD' #precip null, pressure tendency 0, tornado true
remark4 = 'AO2A WATERSPOUT' #precip null, pressure null, tornado true

def test_set_one_hr_rainfall():
    assert_equal(metar.setOneHrPrecip(remark1),0.00)
    assert_equal(metar.setOneHrPrecip(remark2),1.05)
    assert_equal(metar.setOneHrPrecip(remark3),None)
    assert_equal(metar.setOneHrPrecip(remark4),None)

def test_set_three_hr_pressure_tendency():
    assert_equal(metar.setThreeHrPressureTendency(remark1),1.0)
    assert_equal(metar.setThreeHrPressureTendency(remark2),-4.3)
    assert_equal(metar.setThreeHrPressureTendency(remark3),0.0)
    assert_equal(metar.setThreeHrPressureTendency(remark4),None)

def test_set_tornado_bool():
    assert_equal(metar.setTornado(remark1,wxstring1),False)
    assert_equal(metar.setTornado(remark1,wxstring2),True)
    assert_equal(metar.setTornado(remark2,wxstring1),True)
    assert_equal(metar.setTornado(remark3,wxstring1),True)
    assert_equal(metar.setTornado(remark4,wxstring1),True)

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

