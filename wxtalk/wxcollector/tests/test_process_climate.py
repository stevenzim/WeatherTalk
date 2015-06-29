from nose.tools import *
import os
from wxtalk.wxcollector import processclimate as climate


sundata1 = {"SUNRISE": "646 AM",
            "SUNSET": "740 PM"}
sundata2 = {"SUNRISE": "",
            "SUNSET": ""}
sundata3 = {"SUNRISE": None,
            "SUNSET": None}
#convert sunrise/sunset to minutes
def test_set_total_minutes_sun():
    assert_equal(climate.setSunToMins(sundata1["SUNRISE"],sundata1["SUNSET"]),774)
    assert_equal(climate.setSunToMins(sundata2["SUNRISE"],sundata2["SUNSET"]),-999)        
    assert_equal(climate.setSunToMins(sundata3["SUNRISE"],sundata3["SUNSET"]),-999)
    
winddata1 = 11.5
winddata2 = -999.9
winddata3 = ""

#convert winds to knots
def test_set_winds_to_knots():
    assert_equal(climate.setWindsToKnots(winddata1),10.0)
    assert_equal(climate.setWindsToKnots(winddata2),-999.9)
    assert_equal(climate.setWindsToKnots(winddata3),-999.9) 

tempdata1 = 44.0
tempdata2 = -999.9
tempdata3 = ""

#convert temps to celsius
def test_set_temps_celsius():
    assert_equal(climate.setTempsToCelsius(tempdata1),6.7)
    assert_equal(climate.setTempsToCelsius(tempdata2),-999.9)
    assert_equal(climate.setTempsToCelsius(tempdata3),-999.9) 
    
    
#test conversion to utc date stampe
date1 = {'icao':'KSFO',
         'date':'2015-04-01'}
date2 = {'icao':'KJFK',
         'date':'2015-03-31'}
date3 = {'icao':'',
         'date':''}
def test_set_date_to_datetime():
    assert_equal(climate.setDateToDatetime(date1['icao'],date1['date']),['2015-04-01 08:00:00','2015-04-02 07:59:59'])
    assert_equal(climate.setDateToDatetime(date2['icao'],date2['date']),['2015-03-31 05:00:00','2015-04-01 04:59:59'])
    assert_raises(ValueError,\
                climate.setDateToDatetime,date3['icao'],date3['date'])
    


