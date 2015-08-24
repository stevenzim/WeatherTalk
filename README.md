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
    -   System built with Python 2.7.4, Scikit Learn 0.17, numpy 1.9.2, NLTK 3.0.2, TwitterAPI 2.3.3, psycopg2 2.4.5
    -   See notes in README.md files in main and subdirectories as well as doc strings in code for useful information


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
- Run the weather collection script every 5 minutes (unix command provided)
```
while true
do 
    python wxtalk/wxcollector/collectors/metar/rawMETARcollector.py
    sleep 300
done
```

1. When ready to process METAR reports and load into database (e.g. after several days) run the following


How to Collect & Process NWS Climate Data
--------------------

How to Build Sentiment Classifier Models
--------------------

How to Build Weather Topic Classifier Models
----------------------

How to Run Classification and Tweet Linking Pipeline
----------------------


TODO(Future Work):
-----
- Allow for aribitrary DB credentials rather than hard coding





