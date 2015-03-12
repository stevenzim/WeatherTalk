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
                    "possibly_sensitive",\
                    "retweet_count",\
                    "retweeted",\
                    "source",\
                    "truncated"]


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
            cleanedTweetList.append(dropKeysVals(tweet,primaryKeysToDrop))
        else:
            continue
    return cleanedTweetList

def getRawTweets():
    inDirName = '1-RawTweets'
    outDirName = '2-CleanedTweets'
    fileList = helper.getListOfFiles(inDirName)
    utc_datetime = datetime.datetime.utcnow().strftime("%Y-%m-%d-%H%M%SZ")
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
    



while True:
    try:
        getRawTweets()
    except:
        continue