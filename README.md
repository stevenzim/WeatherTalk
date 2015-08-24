 WeatherTalk
==============   
Overview
--------------   
    The included code in this project is for MSc Thesis to retrieve tweets and weather data,
    classify tweets for sentiment and topic(is it related to weather), link tweet to nearest weather report.
    Further analysis can then be performed to determine any possibile links between sentiment scores and the weather.
    
    The overall goals of this package is to provide the abilities to 
    1. Build sentiment and weather topic classification models for tweets
    2. Retrive weather data
    3. Link weather to each tweet
    4. Classifiy new tweets
    5. Load tweets and weather data into database which can be used for further analysis
    
Requirements
--------------  
-   **WeatherTalk** Source Folder **MUST** be in python path directory.  Full packaging is not completed at this time, this is the best workaround.
        -For packaging to work must update ~/.bashrc with following:
        -set PYTHON PATH necessary for weathertalk
        -see stackoverflow "permanently add a directory to python path"
        -export PYTHONPATH="${PYTHONPATH}:/home/steven/Desktop/T/WeatherTalk"
-   PostgreSQL server must be installed with weather database and usernames (default is steven/steven). See wxtalk/resources/db/PostgreNotes for setup notes
-   see dependencies in setup.py 
-   Additional Notes:
    -   System built with Python 2.7.4, Scikit Learn 0.17, numpy 1.9.2, NLTK 3.0.2, TwitterAPI 2.3.3, psycopg2 2.4.5
    -   See notes in README.md files in main and subdirectories as well as doc strings in code for useful information


How to setup DB
--------------
1. In addition to installation of database, scripts must be run to create tables in database
2. Scripts are found in wxtalk/db
3. Run the following
    - from wxtalk.db import (createTwitterTable,createClimateTable, createMetarTable, loadDBwithStations)
    - loadDBwithStations.createStationTable('wxtalk\resources\WeatherStations\FullMasterStation.csv')
    - createClimateTable.createClimateTable()
    - createMetarTable.createMetarTable()
    - createTwitterTable.createTwitterTable()

Collect Raw Tweets
--------------    
1. open python in command line
2. from wxtalk.tweetcollector import main
- All tweets are collected for bounding box in lower 48 United States (can easily be updated in code)
- REQUIRES: A twitter account and api key
    - Update the twitter.creds file in tweetcollector folder with api credentials
    - Rename file to my.creds
- All files are processed into WeatherTalk/pipeline/ 0-RawTweets & 1-CleanedTweets folders
- NOTE: The script will run continually until command window is killed

Collect & Process METAR Weather Data
--------------------

Collect & Process NWS Climate Data
--------------------

Build Sentiment Classifier Models
--------------------

Build Weather Topic Classifier Models
----------------------

Run Classification and Tweet Linking Pipeline
----------------------


TODO:
-----
- Allow for aribitrary DB credentials rather than hard coding


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
