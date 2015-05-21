#script used to grab tweets over a geographical box from the twitter streaming api
from TwitterAPI import TwitterAPI
import json
import datetime
import helper

dirName = '1-RawTweets'

#retrieve twitter credentials
#must fill in blanks of creds file with your keys and secrets supplied by twitter
creds = helper.loadJSONfromFile('my.creds')

def getTweets():
    api = TwitterAPI(consumer_key = creds['consumer_key'], consumer_secret = creds['consumer_secret'], access_token_key = creds['access_token_key'], access_token_secret = creds['access_token_secret'])
    #Grab tweets over CONUS
    request = api.request('statuses/filter', {'locations':'-124.7,24.4,-67,49'})
    #Grab tweets over EASTERN MASS and RI and Nashua NH:
    #request = api.request('statuses/filter', {'locations':'-73.0,40.0,-70,43.0'})

    #initialize variables for new set of 1000 tweets
    utc_datetime = datetime.datetime.utcnow().strftime("%Y-%m-%d-%H%M%SZ")
    fileName = dirName + '/' + 'Tweets_%s.json' % utc_datetime
    totalTweets = 0
    tweetsThisFile = 0
    tweetList = []
    
    #build a list of tweet data.  When a thousand tweets collected, dump to json file
    for currentTweet in request:
        utc = datetime.datetime.utcnow()
        totalTweets +=1
        tweetList.append(currentTweet)
        if (totalTweets % 100) == 0:
            print totalTweets
        if (totalTweets % 1000) == 0:
            helper.dumpJSONtoFile(fileName,tweetList)
            tweetList = []
            return 0

