# WeatherTalk
Contains scripts&amp;code to retrieve WX data and Tweets

INCLUDES:
#  A python package for extracting reported daily climatology from the 
#	 US National Weather Service (NWS) daily climate report
# 
#	 These products are issued daily and provide information such as hi/lo temps
#  precip/snow totals, observed weather, total cloud cover, etc.
#
#  The NCDC http://www.ncdc.noaa.gov/cdo-web/datasets provides official climate data
#
#  These NWS daily climate reports are unofficial.  However, the reports are still very useful
#  1) They have derived products, such as average cloud cover, which are not easily available from NCDC
#  2) They are relevant for 0000 - 2359 local time, which is important if you want to know the highs and lows specific
#     to the relative time at the location.  WMO (World Meteorological Org) and NCDC data is reported in UTC, with max/mins
#			recorded in the 12Z - 12Z period.  As such, the NWS report is a much more relevant report to people living near the station
#
#  At the moment, all precip and temp values in this report are in inches and fahrenheit respectively, but could be easily convertedValue
#
#  This class has only been tested for the stations in MasterStationList provided in project 
#  The reports for all stations have different formats, this module attempts to handle the dynamic nature of these reports.  
#  There are additonal stations which produce reports not in MasterStationList, however they have been excluded
#  because they are not official WMO/ICAO/METAR stations
#
#  The most recent Climate report for a given station is available at the URL where officeID could be any 3 letter code for offices
#  that issue daily reports and climStationID is 3 letter code for actual station.  See MasterStationList for details
#  http://www.weather.gov/climate/getclimate.php?date=&wfo=' + officeID +'&sid='+ climStationID + '&pil=CLI&recent=yes'