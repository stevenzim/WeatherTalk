from wxtalk import helper, pipeline
import time
from wxtalk.modelbuilder import transformers as tran
from wxtalk import helper
import sklearn.externals.joblib as joblib
from wxtalk.db import dbfuncs as db

#example to convert raw tweets to tweets with wx from nearest station
def convertTweetsSimple():
    tweetListofdicts = helper.loadJSONfromFile('cleanTweets.json')
    tweetListWithWxStations = pipeline.getTweetWxStations(tweetListofdicts)
    tweetsWithWx = []
    for dict in tweetListWithWxStations: 
        try:
            tweetsWithWx.append(pipeline.getTweetWxReport(dict))
        except:
            print dict
        
        
#example to take a set of json files of tweets and load them with wx reports and stations
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
    
    errorFile = open("errorFile.log","a")
    
    print str(totalFiles) + " total tweet files will be processed starting now...."
    
    for file in files:
        st_getstation_time = time.time()
        tweetListWithWxStations = []
        try:
            currentListOfTweets = helper.loadJSONfromFile(inFilePath + file)
            print str(len(currentListOfTweets)) + " tweets to process in " + file + "."
            tweetListWithWxStations = pipeline.getTweetWxStations(currentListOfTweets,stationTable = "climateStations")
            #tweetListWithWxStations = pipeline.getTweetWxStations(currentListOfTweets,stationTable = "metarStations")
            filesProcessed +=1
            print "Total files remaining = " + str(totalFiles - filesProcessed)
        except:
            fileErrors +=1
            errorFile.write("Error: getTweetWxStations for file: " + file)
            continue
        
        print("Get Stations time--- %s seconds ---" % (time.time() - st_getstation_time))
        print
        
        st_getwxreport_time = time.time()
        tweetsWithWx = []
        for dict in tweetListWithWxStations: 
            try:
                tweetsWithWx.append(pipeline.getTweetWxReport(dict))
                totalTweetsProcessed +=1
            except:
                totalTweetErrors += 1
                #helper.dumpJSONtoFile(inFilePath + 'errors/' + str(totalTweetErrors) + "-" + file,dict)
                errorFile.write("Error: getTweetWxReport for file: " + file + " and tweet ID: " + str(dict["id"]) + "\n")
                continue
        helper.dumpJSONtoFile(outFilePath + file,tweetsWithWx)
        print("Get Wx Report time--- %s seconds ---" % (time.time() - st_getwxreport_time))
        print
        print("Total elapsed time--- %s seconds ---" % (time.time() - start_time))
    
    print str(filesProcessed) + " files processed with error files = " + str(fileErrors)
    print str(totalTweetsProcessed) + " tweets processed with tweet errors = " + str(totalTweetErrors)  
    print("completed in--- %s seconds ---" % (time.time() - start_time))
    
    errorFile.close()
    
    
#example to take a set of json files of tweets with weather reports and then classify sentiment of tweet
def getSentiment():
    start_time = time.time()
    inFilePath = "3-TweetsWithWx/"
    outFilePath = "4-TweetsWxClassified/"
    files = helper.getListOfFiles(inFilePath)
    totalTweetsProcessed = 0
    totalTweetErrors = 0
    
    totalFiles = len(files)
    filesProcessed = 0
    fileErrors = 0
    
    errorFile = open("classify-errorFile.log","a")
    
    print str(totalFiles) + " total tweet files will be processed starting now...."

    
    for file in files:
        st_getsentiment_time = time.time()
        try:
            print
            print
            print file + " is being processed for sentiment prediction."
            helper.extractTweetNLPtriples(inFilePath + file,inFilePath +'temp/tempTweetsTriples.json')
            loadedpipe = joblib.load('pickles/test.pkl')
            data = helper.loadJSONfromFile(inFilePath +'temp/tempTweetsTriples.json')           
            ed = tran.TriplesYsExtractor()
            triplesList = ed.transform(data)
            predicted_ys = loadedpipe.predict(triplesList)
            sentimentList = predicted_ys.tolist()
            count = 0
            totalTweetsProcessed += len(data) 
            for dict in data:
                keydropped = dict.pop("tagged_tweet_triples",None)  #stored as variable in order to supress print to screen
                dict["sentiment_score"] = sentimentList[count]
                count += 1

            helper.dumpJSONtoFile(outFilePath + file,data)   #dump live tweets with classifer predictions added to json

            filesProcessed +=1
            print "Total files remaining = " + str(totalFiles - filesProcessed)
        except:
            fileErrors +=1
            errorFile.write("Error: getTweetSentiment for file: " + file +"\n")
            continue
        
        print("Get Sentiment time--- %s seconds ---" % (time.time() - st_getsentiment_time))

        print("Total elapsed time--- %s seconds ---" % (time.time() - start_time))
    
    print str(filesProcessed) + " files processed with error files = " + str(fileErrors)
    print str(totalTweetsProcessed) + " tweets processed."
    print("completed in--- %s seconds ---" % (time.time() - start_time))
    
    errorFile.close()

def prepTweetsDb():
    start_time = time.time()
#    inFilePath = "4-TweetsWxClassified/temp/"
#    outFilePath = "5-TweetsReadyForDB/temp/"
    inFilePath = "4-TweetsWxClassified/"
    outFilePath = "5-TweetsReadyForDB/"
    files = helper.getListOfFiles(inFilePath)
    totalTweetsProcessed = 0
    totalTweetErrors = 0
    
    totalFiles = len(files)
    filesProcessed = 0
    fileErrors = 0
    
    errorFile = open("tweetDb-errorFile.log","a")
    
    print str(totalFiles) + " total tweet files will be processed starting now...."        
    for file in files:
        file_time = time.time()
        try:
            print
            print
            print file + " is being processed for db."
            data = helper.loadJSONfromFile(inFilePath +file)           
            totalTweetsProcessed += len(data) 
            for dict in data:
                keysToDrop = ["in_reply_to_status_id","in_reply_to_user_id","lang","metar_report","timestamp_ms","user","text"]
                #keysToDrop = ["in_reply_to_status_id","in_reply_to_user_id","lang","metar_report","timestamp_ms","user"]
                dict['user_id'] = dict['user']['id']
                dict['user_name'] = dict['user']['screen_name']
                dict['coordinates'] = str(tuple(dict['coordinates']['coordinates']))
                #pop the list of keys, these key names are not columns in db.
                for key in keysToDrop:
                    temp = dict.pop(key,None)  #stored as variable in order to supress print to screen

            helper.dumpJSONtoFile(outFilePath + file,data)   #dump updated tweets to file

            filesProcessed +=1
            print "Total files remaining = " + str(totalFiles - filesProcessed)
        except Exception as error:
            fileErrors +=1
            errorFile.write("Error: prepTweetsDb for file: " + file +"\n")
            errorFile.write(str(error) + '\n')
            print "Check tweetdb-errorFile.log"
            continue
        
        print("Current file prep time--- %s seconds ---" % (time.time() - file_time))

        print("Total elapsed time--- %s seconds ---" % (time.time() - start_time))
    
    print str(filesProcessed) + " files processed with error files = " + str(fileErrors)
    print str(totalTweetsProcessed) + " tweets processed."
    print("completed in--- %s seconds ---" % (time.time() - start_time))
    
def batchLoadTweets():
    '''Provided a directory path containing full processed/classified tweets.'''
    start_time = time.time()
    #inFilePath = "5-TweetsReadyForDB/temp/"
    inFilePath = "5-TweetsReadyForDB/"
    files = helper.getListOfFiles(inFilePath)
    totalTweetsProcessed = 0
    totalTweetErrors = 0
    
    totalFiles = len(files)
    filesCompleted = 0
    fileErrors = 0
    
    errorFile = open("tweetDb-errorFile.log","a")
    
    #db setup
    s = db.Tweet()
    
    print str(totalFiles) + " total tweet files will be processed starting now...."        
    for file in files:

        totalTweetsInFileProcessed = 0
        file_time = time.time()
        try:    
            print
            print
            print file + " is being processed for db."
            data = helper.loadJSONfromFile(inFilePath +file)   
            totalTweetsInFile = len(data)  

            for dict in data:    
                #print dict
                try:
                    s.loadTweet(dict)
                    totalTweetsProcessed+=1
                    totalTweetsInFileProcessed+=1
                    #print "Loading tweet to db"
                except Exception as error:
                    #TODO: fix error logging, currently it is logging way to much
                    #logger1.error('Error load dict via loadMetarReport: %s',  dict)
                    s = db.Tweet()
                    totalTweetErrors+=0
                    
                    #print "Im here"
                    errorFile.write(str(error) + '\n')
                    #print "Now i am here"
                    continue
            filesCompleted += 1
            if (totalTweetsInFileProcessed % 100) == 0:
                print str(totalTweetsInFileProcessed) + " tweets loaded for current file of total tweets = " + str(totalTweetsInFile)
        except Exception as error:
            fileErrors +=1
            errorFile.write("Error: prepTweetsDb for file: " + file +"\n")
            errorFile.write(str(error) + '\n')
            print "Check tweetdb-errorFile.log"
            continue
        print str(filesCompleted) + " files loaded of " + str(totalFiles) + ". Current file = " + file
        print str(totalTweetsProcessed) + " tweets loaded into DB. With total tweet errors = " + str(totalTweetErrors)
        print("Current file prep time--- %s seconds ---" % (time.time() - file_time))

        print("Total elapsed time--- %s minutes ---" % (((totalFiles - (filesCompleted+fileErrors))*(time.time() - start_time))/60.)
        print "Total files remaining = " + str(totalFiles - (filesCompleted+fileErrors))
        print "Estimated time remaining in minutes = " + str(((totalFiles - (filesCompleted+fileErrors))*(time.time() - file_time))/60.)
    
    print str(filesCompleted) + " files processed with error files = " + str(fileErrors)
    print str(totalTweetsProcessed) + " tweets loaded into DB. With total tweet errors = " + str(totalTweetErrors)
    print("Total completion time in minutes--- %s minutes ---" % ((time.time() - start_time)/60.))   



#very hacky example to produce a csv output of tweet json file with wx and sentiment scores.    
def dumpDictToCsv():
    import csv
    inFilePath = "csv/"
    my_list_dicts = helper.loadJSONfromFile(inFilePath +'test.json')
    for my_dict in my_list_dicts:
        #my_dict = my_list_dicts[0]
        my_dict["coordinates"] = my_dict["coordinates"]["coordinates"]
        my_dict["coord_lon"] = my_dict["coordinates"][0]
        my_dict["coord_lat"] = my_dict["coordinates"][0]
        my_dict["user"] = my_dict["user"]["id"]
        metar = my_dict["metar_report"][:-1]
        my_dict.pop("metar_report")
        my_dict.pop("text")
        fieldCount = 0
        for field in metar:
            if fieldCount <10:
                my_dict["metar_0" + str(fieldCount)] = field
            else:
                my_dict["metar_" + str(fieldCount)] = field
            fieldCount += 1
            
        my_dict.pop("metar_20")
        my_dict.pop("metar_21")
        with open('mycsvfile.csv', 'a') as f:  # Just use 'w' mode in 3.x
            w = csv.DictWriter(f, sorted(my_dict))
            #w.writeheader()
            w.writerow(my_dict)    

