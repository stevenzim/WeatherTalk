from wxtalk import helper
'''Script to combine Semeval and Kaggle data for weather topic training'''
fs = helper.getListOfFiles('.')
outputList = []

#confirm no duplicate tweets, append to list if not duplicate and then dump to full file

def dedupeCombineSemeval():
    totalSemeval = 0
    totalDupes = 0
    idMasterList = []
    deduplicatedTweets = []
    for f in fs:
        data = helper.loadJSONfromFile(f)
        print str(len(data)) + " tweets in " + f
        totalSemeval += len(data)
        for tweet in data:
            if tweet['tweet_id'] in idMasterList:
                print tweet['tweet_id'] + " is a dupe tweet found in " + f
                totalDupes += 1
            else:
                idMasterList.append(tweet['tweet_id'])
                deduplicatedTweets.append(tweet)
    helper.dumpJSONtoFile("CombinedSemeval.json",deduplicatedTweets)
    print "Total Semeval Tweets: " + str(totalSemeval)
    print "Total Dupes: " + str(totalDupes)


#make the semeval json files similar to Kaggle data set classes.  We assume that topic is always false 
def matchKaggleFormat():
    outputList = []        
    data = helper.loadJSONfromFile('CombinedSemeval.json')
    print len(data)
    for d in data:
        d["topic_wx_00"] = False
        d["topic_wx_10"] = False
        d["topic_wx_20"] = False
        d["topic_wx_30"] = False
        d["topic_wx_40"] = False
        d["topic_wx_50"] = False
        d["topic_wx_60"] = False
        d["topic_wx_70"] = False
        d["topic_wx_80"] = False
        d["topic_wx_90"] = False
        d["topic_wx_100"] = False
        d["source"] = "Semeval"
        outputList.append(d)
        
    helper.dumpJSONtoFile('CombinedSemeval.json',outputList)

#get 500 random tweets to validate percentage about weather
from random import shuffle
from wxtalk import helper
def produceSampling():
    data = helper.loadJSONfromFile('CombinedSemeval.json')
    shuffle(data)
    tweetText500 = map(lambda tweet: (tweet['text']),data[0:500])
    oFile = open("500-tweets.csv",'w')
    oFile.write("About Weather?, Tweet Text"+ '\n')
    for tweet in tweetText500:
        oFile.write(",\""+tweet + '\"\n')
    oFile.close()


fs = ['TestWeather.json', 'DevWeather.json', 'TrainWeather.json']
def combineBoth():
    '''Splits based on approx percentages for semeval task'''
    alldata = []
    for f in fs:
        data = helper.loadJSONfromFile(f)
        print len(data)
        for d in data:
            alldata.append(d)
    shuffle(alldata)
    print len(alldata)
    helper.dumpJSONtoFile('TrainWeather.json',alldata[:68000]) #split ~70% Training
    helper.dumpJSONtoFile('DevWeather.json',alldata[68000:81500]) #split ~15% Dev
    helper.dumpJSONtoFile('TestWeather.json',alldata[81500:]) #split ~15% Test


def createTriplesFiles():
    '''Create NLP Triple files for each split file'''
    for inFile in fs:
        outFile = inFile.split('.')
        outFile = outFile[0] + 'Triples.' + outFile[1]
        helper.extractTweetNLPtriples(inFile,outFile)


from wxtalk import helper
'''Script to change id to tweet_id'''
fs = helper.getListOfFiles('.')

for f in fs:
    iFile.open(f,'r')
    oFile.open("n" + f,'w')
    for line in iFile:
        line = line.replace('"id":','"tweet_id":')
        oFile.write(line)
    iFile.close()
    oFile.close()


