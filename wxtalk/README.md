wxtalk Descriptions
---------------------
- db: Contains functions to create database tables and perform queries on database
- errors: error folder
- externals: Contains any additional external libraries (e.g. TweetNLP wrapper)
- model: Most important components of system.  Includes transformers to extract features
    predictors to take binary models and make predictions on unseen data
    ensemblers, to combine model predictions into model and make final predictions
- resources: Contains necessary resources for system (see README.md files in subfolder)
- tests: Contains tests for wxtalk/helper.py  and wxtalk/pipeline.py
- tweetcollector: Functions to retrieve tweets from twitter api
- wxcollector: Contains functions to retrieve weather data: METAR and NWS climate reports
- helper.py: contains useful helper functions for system
- pipeline.py: contains pipeline functions (i.e. dedupe & load metar data into db,
    find nearest weather station to tweet and also find uid of correct METAR and climate reports
    based on time of tweet)


