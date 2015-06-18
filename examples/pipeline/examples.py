from wxtalk import helper, pipeline
import time

#example to convert raw tweets to tweets with wx from nearest station
tweetListofdicts = helper.loadJSONfromFile('cleanTweets.json')
tweetListWithWxStations = pipeline.getTweetWxStations(tweetListofdicts)
tweetsWithWx = []
for dict in tweetListWithWxStations: 
    try:
        tweetsWithWx.append(pipeline.getTweetWxReport(dict))
    except:
        print dict
        
        
#complex example to take a set of json files of tweets and loading them with wx reports
import time
def getWx():
    start_time = time.time()
    inFilePath = "2-CleanedTweets/"
    outFilePath = "3-TweetsWithWx/"
    files = helper.getListOfFiles(inFilePath)
    totalTweetsProcessed = 0
    totalTweetErrors = 0
    
    totalFiles = len(files)
    filesProcessed = 0
    fileErrors = 0
    print str(totalFiles) + " total tweet files will be processed starting now...."
    
    for file in files:
        tweetListWithWxStations = []
        try:
            currentListOfTweets = helper.loadJSONfromFile(inFilePath + file)
            print str(len(currentListOfTweets)) + " tweets to process in " + file + "."
            tweetListWithWxStations = pipeline.getTweetWxStations(currentListOfTweets)
            filesProcessed +=1
            print "Total files remaining = " + str(totalFiles - filesProcessed)
        except:
            fileErrors +=1
            continue
        
        tweetsWithWx = []
        for dict in tweetListWithWxStations: 
            try:
                tweetsWithWx.append(pipeline.getTweetWxReport(dict))
                totalTweetsProcessed +=1
            except:
                totalTweetErrors += 1
                continue
        helper.dumpJSONtoFile(outFilePath + file,tweetsWithWx)
        print("elapsed time--- %s seconds ---" % (time.time() - start_time))
    
    print str(filesProcessed) + " files processed with error files = " + str(fileErrors)
    print str(totalTweetsProcessed) + " files processed with error files = " + str(totalTweetErrors)  
    print("completed in--- %s seconds ---" % (time.time() - start_time))
