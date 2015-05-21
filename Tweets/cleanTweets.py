#Steven Zimmerman
#21-MAY-2015

#This is a script to clean up my collected raw twitter data into the desired 
#format.   Many unnecessary keys are dropped.  Most important of all......
#only tweets with user location coordinates are kept, all others are discarded. 
#NOTE: On April 27th - Twitter implemented changes to the way locations are
# reported.   Prior to this, ~80% of tweets were had specific user coordinates.
# Post this, ~20% of tweets had specific user coordinates. For more information:
#search for '80% reduction in tweets' on https://twittercommunity.com/

from TwitterAPI import TwitterAPI
import json
import datetime
import helper

#keys to drop
primaryKeysToDrop = ["contributors",\
                    "entities",\
                    "extended_entities",\
                    "favorite_count",\
                    "favorited",\
                    "filter_level",\
                    "geo",\
                    "id_str",\
                    "in_reply_to_screen_name",\
                    "in_reply_to_status_id_str",\
                    "in_reply_to_user_id_str",\
                    "place",\
                    "possibly_sensitive",\
                    "retweet_count",\
                    "retweeted",\
                    "source",\
                    "truncated"]
                    
userKeysToDrop =    ["contributors_enabled",\
                    "created_at",\
                    "default_profile",\
                    "default_profile_image",\
                    "description",\
                    "favourites_count",\
                    "follow_request_sent",\
                    "following",\
                    "friends_count",\
                    "geo_enabled",\
                    "id_str",\
                    "is_translator",\
                    "lang",\
                    "listed_count",\
                    "location",\
                    "name",\
                    "notifications",\
                    "profile_background_color",\
                    "profile_background_image_url",\
                    "profile_background_image_url_https",\
                    "profile_background_tile",\
                    "profile_banner_url",\
                    "profile_image_url",\
                    "profile_image_url_https",\
                    "profile_link_color",\
                    "profile_sidebar_border_color",\
                    "profile_sidebar_fill_color",\
                    "profile_text_color",\
                    "profile_use_background_image",\
                    "protected",\
                    "statuses_count",\
                    "time_zone",\
                    "url",\
                    "verified"]


# primaryKeysToDrop = ["place",\
                    # "user",\
                    # "truncated"]



#nested sub-keys to drop




def getVals(dictionary, key):
    '''Useful for nested maps. Returns the values from dictionary given the 
    specified key and is a prettier/more readable way to do this task'''
    #TODO: Perhaps a better way to do this???
    try:
        return dictionary[key]
    except:
        return False

def dropKeysVals(dictionary, keysToDrop):
    '''Remove specified Keys and Values from dictionary based on provided list'''
    for keyName in keysToDrop:
        try:
            dictionary.pop(keyName)
        except:
            continue
    return dictionary
    
def criterianTest(tweet):
    '''
    Tweet must be in english, in USA and have coordinates
    '''
    #tests to pass, otherwise advance to next tweetList
    #"coordinates": null                IF VAL IS NULL THEN TEST FAILS
    #"lang": "en"                       IF VAL != english  THEN TEST FAILS
    #"place" --> "country_code": "US"   IF COUNTRY NOT US THEN TEST FAILS
    
    if getVals(tweet,"coordinates") == None:        #confirm coordinates exist
        return False
    if str(getVals(tweet,"lang")).lower() != 'en':   #confirm English is language
        return False
    if str(getVals(getVals(tweet,"place"),"country_code")).lower() != 'us': #confirm country is USA
        return False
    return True


def cleanRawTweets(rawTweetList,cleanedTweetList):
    for tweet in rawTweetList:
        if criterianTest(tweet):
            cleanedUser = dropKeysVals(getVals(tweet,"user"),userKeysToDrop)
            tweet["user"] = cleanedUser
            cleanedTweetList.append(dropKeysVals(tweet,primaryKeysToDrop))
        else:
            continue
    return cleanedTweetList

    #TODO: need a better name or reorg so that get raw tweets is list of files
def getRawTweets():
    inDirName = '1-RawTweets'
    outDirName = '2-CleanedTweets'
    fileList = helper.getListOfFiles(inDirName)
    utc_datetime = datetime.datetime.utcnow().strftime("%Y-%m-%d-%H%M-%SZ")
    outFileName = outDirName + '/' + 'Tweets_%s.json' % utc_datetime
    totalTweets = 0
    tweetsThisFile = 0
    cleanedTweetList = []
    filesProcessed = []
    
    if len(fileList) == 0:
        #print "No Files to Process"
        return False
    for file in fileList:
        #TODO: Need to handle situation if file still open or not json
        path = inDirName + '/' + file
        rawTweetList = helper.loadJSONfromFile(path)
        #print file
        cleanedTweetList = cleanRawTweets(rawTweetList,cleanedTweetList)
        #helper.dumpJSONtoFile(outFileName,cleanedTweetList)
      
        filesProcessed.append(file)
    print len(cleanedTweetList)
    print filesProcessed
    helper.deleteFilesInList(inDirName,filesProcessed)
    helper.dumpJSONtoFile(outFileName,cleanedTweetList)
        #if len(cleanedTweetList) > 10000:
            #TODO: A better way to do this would be to sum the totals in input filesProcessed
            #       Thus preventing duplication and/or data loss
            #a cheap way to prevent memory overflow
        #    break
    

    
    #
    



