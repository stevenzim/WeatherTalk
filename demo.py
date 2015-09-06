from processing import mainpipe as pipe
from wxtalk import helper
from wxtalk import pipeline

import sys
import pprint
import json


fileName = "demo.json"

#demo text classification
def demoClassify(demoText):
    demoDict = [{"text" : demoText}]
    
    helper.dumpJSONtoFile(helper.getProjectPath() + "/processing/3-TweetsWithWx/demo.json", demoDict)
    
    print "Classifying tweet"
    pipe.classifyTweets()
    
    demoClassifiedTweets = helper.loadJSONfromFile(helper.getProjectPath() + "/processing/4-ClassifiedTweets/demo.json")
    
    pprint.pprint(demoClassifiedTweets)

#demo weather station finder
def demoStations(lon,lat):
    demoTweet = [{
            "coordinates": {
                "coordinates": [
                    lon,
                    lat
                ]}}]
                
    stations = pipeline.getTweetWxStations(demoTweet)
    print json.dumps(stations,sort_keys=True, indent=4)
