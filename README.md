 WeatherTalk
==============   
Overview
--------------   
The included code in this project is for MSc Thesis to retrieve tweets and weather data,
classify tweets for sentiment and topic(is it related to weather), link tweet to nearest weather report.
Further analysis can then be performed to determine any possibile links between sentiment scores and the weather.

###The overall goals of this package include:
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
    -   System built with Python 2.7.4, Scikit Learn 0.17, numpy 1.9.2, 
    NLTK 3.0.2, TwitterAPI 2.3.3, psycopg2 2.4.5 and flatdict 1.1.3
    -   See notes in README.md files in main and subdirectories 
    as well as doc strings in code for useful information


How to setup DB
--------------
1. In addition to installation of database, scripts must be run to create tables in database
2. Scripts are found in wxtalk/db
3. Run the following
```
from wxtalk.db import (createTwitterTable,createClimateTable, createMetarTable)
from wxtalk.db importloadDBwithStations
loadDBwithStations.createStationTable('wxtalk\resources\WeatherStations\FullMasterStation.csv')
createClimateTable.createClimateTable()
createMetarTable.createMetarTable()
createTwitterTable.createTwitterTable()
```
- Code will have to be modified for different database username/passwords


How to Collect Raw Tweets
--------------    
open python in command line and run
```
from wxtalk.tweetcollector import main
```

- All tweets are collected for bounding box in lower 48 United States 
(can easily be updated in code)
- REQUIRES: A twitter account and api key
    - Update the twitter.creds file in tweetcollector folder with api credentials
    - Rename file to my.creds
- All files are processed into WeatherTalk/pipeline/ 0-RawTweets & 1-CleanedTweets folders
- NOTE: The script will run continually until command window is killed

How to Collect & Process METAR Weather Data
--------------------
- Run the weather collection script every 5 minutes (scheduled job or similar). 
unix command example:
```
while true
do 
    python wxtalk/wxcollector/collectors/metar/rawMETARcollector.py
    sleep 300
done
```
- When ready to process METAR reports and load into database 
(e.g. after several days of collection and prior to loading tweets) 
run the following from python command window:
```
from wxtalk import pipeline
pipeline.removeDuplicateMetar()
pipeline.batchLoadMetarReports()
```


How to Collect & Process NWS Climate Data
--------------------
- Run the weather collection script every 60 minutes as reports are updated
throughout the day and to provide coverage for network failures. Run as a 
scheduled job or similar. 
unix command example:
```
while true
do 
    python wxtalk/wxcollector/collectors/climReport/retrieveClimateReports.py
    sleep 3600
done
```
- When ready to process NWS climate reports and load into database 
(e.g. after several days of collection and prior to loading tweets) 
run the following from python command window:
```
from wxtalk.wxcollector import processclimate
processclimate.processAndAggregate()
processclimate.loadClimateReportsToDB()
```

How to Run Classification and Tweet Linking Pipeline
----------------------
- These steps are to be performed only after loading weather reports into 
database. You must have reports loaded with time stamps that occur prior to the 
time stamp of tweet, otherwise linking will not occur.
- Run the following command in python command window (~1000 tweets per minute)
```
from processing import mainpipe
mainpipe.organizeTweets()
mainpipe.getWx()
mainpipe.classifyTweets()
mainpipe.loadTweetsToDB()
```


How to Build & Evaluate Classification Models
--------------------
- Code is provided that was used to extract, evaluate and produce model binaries
This code can be modified to produce different models.
- For code to produce final sentiment models see 
modelbuilders/2013Semeval-FinalPipes.py
- For code to produce final sentiment models see 
modelbuilders/WxPipes.py
- For evaluation, the modelbuilders/scorer.py provided by SemEval 2013 was used
in command prompt enter python B predictionFileName goldFileName


TODO(Future Work):
-----
- Allow for aribitrary DB credentials rather than hard coding
- Improve pipeline of tweet processing to better handle time stamp situations
- Add multi thread processing
- Improve station search (distance search on 2000 stations is a very expensive
operation, as such a better method to find nearest stations would speed up 
the overall search)





