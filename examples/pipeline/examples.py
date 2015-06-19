from wxtalk import helper, pipeline
import time
from wxtalk.modelbuilder import transformers as tran
from wxtalk import helper
import sklearn.externals.joblib as joblib

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
            #tweetListWithWxStations = pipeline.getTweetWxStations(currentListOfTweets,stationTable = "climateStations")
            tweetListWithWxStations = pipeline.getTweetWxStations(currentListOfTweets,stationTable = "metarStations")
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
            errorFile.write("Error: getTweetSentiment for file: " + file)
            continue
        
        print("Get Sentiment time--- %s seconds ---" % (time.time() - st_getsentiment_time))

        print("Total elapsed time--- %s seconds ---" % (time.time() - start_time))
    
    print str(filesProcessed) + " files processed with error files = " + str(fileErrors)
    print str(totalTweetsProcessed) + " tweets processed."
    print("completed in--- %s seconds ---" % (time.time() - start_time))
    
    errorFile.close()
    

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

