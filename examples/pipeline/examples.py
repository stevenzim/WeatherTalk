from wxtalk import helper, pipeline
import time
from wxtalk.modelbuilder import transformers as tran
from wxtalk import helper
import sklearn.externals.joblib as joblib
from wxtalk.db import dbfuncs as db
import os

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

def dumpErrorListOfDicts(filePath,listOfErrorDicts):
    '''Dumps dictionaries to json file, function is to make things look cleaner below'''
    if len(listOfErrorDicts) > 0:
        helper.dumpJSONtoFile(filePath + 'errors/error-dicts-' + helper.getDateTimeStamp(True) + '.json',listOfErrorDicts)        
        
#take a set of json files of tweets and load them with wx reports and stations
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
    
    errorFile = open(inFilePath + "errors/errorFile.log","a")
    
    listOfErrorDicts = []
    listOfCompletedFiles = []
    
    print str(totalFiles) + " total tweet files will be processed to find Wx stations/reports...."
    
    for file in files:
        #get canidate climate and metar stations for tweet
        st_getstation_time = time.time()
        tweetListWithWxStations = []
        try:
            #load json file and dump file to error folder if there is an error e.g. corrupt file
            try:
                currentListOfTweets = helper.loadJSONfromFile(inFilePath + file)
            except:
                os.rename(inFilePath + file,inFilePath +'errors/'+ file)
                errorFile.write("Error Loading JSON file with json helper function in getwx in file: " + file)
                continue
            print str(len(currentListOfTweets)) + " tweets to process in " + file + "."
            #get canidate metar and climate stations for current tweet
            tweetListWithWxStations = pipeline.getTweetWxStations(currentListOfTweets,stationTable = "stations")
            filesProcessed +=1
            print "Total files remaining = " + str(totalFiles - filesProcessed)
        except Exception as error:
            #if there is an error getting stations, then dump file to error folder 
            fileErrors +=1
            os.rename(inFilePath + file,inFilePath +'errors/'+ file)
            errorFile.write("Error for current list of tweets passed to pipe.getTweetWxStations for file: " + file + " ERROR: " + str(error))
            continue
        
        print("Get Stations time--- %s seconds ---" % (time.time() - st_getstation_time))
        print
        
        totalTweetsProcessed += len(tweetListWithWxStations)
        
        #link tweet to metar report
        st_getmetarreport_time = time.time()
        tweetsWithMetar = []
        for dict in tweetListWithWxStations: 
            try:
                tweetsWithMetar.append(pipeline.getTweetMetarReport(dict))
            except Exception as error:
                totalTweetErrors += 1
                dict['ERROR']='Error finding metar report via pipe.getTweetMetarReport, perhaps none was available for station/time combo. Original file = ' + file.split('/')[-1]
                listOfErrorDicts.append(dict)
                #helper.dumpJSONtoFile(inFilePath + 'errors/' + str(totalTweetErrors) + "-" + file,dict)
                #errorFile.write("ERROR: " + str(error) + " Error: getTweetMetarReport for file: " + file + " and tweet ID: " + str(dict["id"]) + "\n")
                continue

        print("Get Metar Report time--- %s seconds ---" % (time.time() - st_getmetarreport_time))


        #link tweet to climate report
        #   This only links tweet occuring in local time window of report (i.e. 24 hours).  That is if the tweet occurs 1 minute after start time of new report
        # Then the uid of the new report is linked to tweet.  This is not ideal, but it is simple, can be further updated in future work.  In analysis, one should consider
        # filtering out tweets where climate delta time is small as the report is representative of only a short window of time for the tweet
        # That said, concern is low, because most tweets do not happen in the couple of hours after start time of report as this is start of local day when most people are sleeping
        # and tweet rates are low
        st_getclimatereport_time = time.time()
        tweetsWithClimate = []
        for dict in tweetsWithMetar: 
            try:
                tweetsWithClimate.append(pipeline.getTweetClimateReport(dict))
            except Exception as error:
                totalTweetErrors += 1
                dict['ERROR']='Error finding climate report via pipe.getTweetClimateReport, perhaps none was available for station/time combo. Original file = ' + file.split('/')[-1]
                listOfErrorDicts.append(dict)
                #helper.dumpJSONtoFile(inFilePath + 'errors/' + str(totalTweetErrors) + "-" + file,dict)
                #errorFile.write("ERROR: " + str(error) + " Error: getTweetClimateReport for file: " + file + " and tweet ID: " + str(dict["id"]) + "\n")
                continue
        if len(tweetsWithClimate) > 0:
            helper.dumpJSONtoFile(outFilePath + file,tweetsWithClimate)
        print("Get Climate Report time--- %s seconds ---" % (time.time() - st_getclimatereport_time))
        print
        print("Total elapsed time--- %s seconds ---" % (time.time() - start_time))
        


        #Dump any remaining errors and log details of current processing to error file      
        dumpErrorListOfDicts(inFilePath,listOfErrorDicts)
        listOfErrorDicts = []
            
        #delete current file from inFile directory, tweets have been processes succesfully and moved to next step, or written to error folder
        helper.deleteFilesInList(inFilePath,[file])
    
    print str(filesProcessed) + " files processed with error files = " + str(fileErrors)
    print str(totalTweetsProcessed) + " tweets processed with tweet errors = " + str(totalTweetErrors)  
    print("completed in--- %s seconds ---" % (time.time() - start_time))
    

    errorFile.write("Total tweets=," + str(totalTweetsProcessed) + ",Total tweets errors=," + str(totalTweetErrors) +\
                      ",Total files processed =," + str(filesProcessed) + ",Total file errors=," + str(fileErrors) + "\n")
    errorFile.close()
    

    
def getTriplesAndTopics():
    start_time = time.time()
    inFilePath = "3-TweetsWithWx/"
    outFilePath = "4-TweetsTriplesTopicsWx/"
    files = helper.getListOfFiles(inFilePath)
    totalTweetsProcessed = 0
    totalTweetErrors = 0
    
    totalFiles = len(files)
    filesProcessed = 0
    fileErrors = 0
    
    errorFile = open(inFilePath + "errors/errorFile.log","a")
    
    listOfErrorDicts = []
    
    print str(totalFiles) + " total tweet files will be processed to find triples/topics starting now...."
    
    for file in files:
        #get nlp triples for each tweet in file
        st_getTriples_time = time.time()
        tweetListWithTriples = []
        try:
            tweetListWithTriples = helper.extractTweetNLPtriples(inFilePath + file)            
            filesProcessed +=1
            print "Total files remaining = " + str(totalFiles - filesProcessed)
        except Exception as error:
            #if there is an error getting stations, then dump file to error folder 
            fileErrors +=1
            os.rename(inFilePath + file,inFilePath +'errors/'+ file)
            errorFile.write("Error Processing JSON file for triples extraction in file: " + file + " With error: " + str(error) + '\n')
            continue
        
        print("Get Triples time--- %s seconds ---" % (time.time() - st_getTriples_time))
        print
        
        #Add simple topics based on string test to dictionary
        #NOTE: If disk space is an issue, this could be done just before loading into db, as this step is fast
        st_getTopics_time = time.time()
        tweetsWithTopics = []
        for dict in tweetListWithTriples: 
            try:
                dict = helper.addStringTestTopic(dict,'text','obama','topic_obama')
                dict = helper.addStringTestTopic(dict,'text','adidas','topic_adidas')
                dict = helper.addStringTestTopic(dict,'text','nike','topic_nike')
                dict = helper.addStringTestTopic(dict,'text','boeing','topic_boeing')
                dict = helper.addStringTestTopic(dict,'text','microsoft','topic_microsoft')
                dict = helper.addStringTestTopic(dict,'text','tableau','topic_tableau')
                dict = helper.addStringTestTopic(dict,'text','verizon','topic_verizon')
                dict = helper.addStringTestTopic(dict,'text','apple','topic_apple')
                dict = helper.addStringTestTopic(dict,'text','samsung','topic_samsung')
                dict = helper.addStringTestTopic(dict,'text','wal-mart','topic_walmart')
                tweetsWithTopics.append(dict)
                totalTweetsProcessed +=1
            except Exception as error:
                totalTweetErrors += 1
                dict['ERROR']='Error adding topic bools. Original file = ' + file.split('/')[-1]
                listOfErrorDicts.append(dict)
                continue
        
        if len(tweetsWithTopics) > 0:
            helper.dumpJSONtoFile(outFilePath + file,tweetsWithTopics)
        print("Get Topics time--- %s seconds ---" % (time.time() - st_getTopics_time))
        print
        print("Total elapsed time--- %s seconds ---" % (time.time() - start_time))

        #Dump any remaining errors and log details of current processing to error file      
        dumpErrorListOfDicts(inFilePath,listOfErrorDicts)
        listOfErrorDicts = []
            
        #delete current file from inFile directory, tweets have been processes succesfully and moved to next step, or written to error folder
        helper.deleteFilesInList(inFilePath,[file])
    
    print str(filesProcessed) + " files processed with error files = " + str(fileErrors)
    print str(totalTweetsProcessed) + " tweets processed with tweet errors = " + str(totalTweetErrors)  
    print("completed in--- %s seconds ---" % (time.time() - start_time))
    

    errorFile.write("Total tweets=," + str(totalTweetsProcessed) + ",Total tweets errors=," + str(totalTweetErrors) +\
                      ",Total files processed =," + str(filesProcessed) + ",Total file errors=," + str(fileErrors) + "\n")
    errorFile.close()
    
   
#example to take a set of json files of tweets with weather reports and then classify sentiment of tweet
def getClassifications():
    start_time = time.time()
    inFilePath = "4-TweetsTriplesTopicsWx/"
    outFilePath = "5-ClassifiedTweets/"
    files = helper.getListOfFiles(inFilePath)
    totalTweetsProcessed = 0
    totalTweetErrors = 0
    
    totalFiles = len(files)
    filesProcessed = 0
    fileErrors = 0
    
    errorFile = open(inFilePath + "errors/errorFile.log","a")
    
    listOfErrorDicts = []
        
    print str(totalFiles) + " total tweet files will be classified starting now...."

    #load sentiment classification model pipeline from pickle files
    loadedpipe = joblib.load('pickles/test.pkl')
    
    #classify all tweets in each file
    for file in files:
        #sentiment classification
        st_getsentiment_time = time.time()
        try:
            print
            print
            print file + " is being processed for sentiment classification."
            
            data = helper.loadJSONfromFile(inFilePath +file)           
            ed = tran.TriplesYsExtractor()  #create transformer object
            triplesList = ed.transform(data)  #extract triples list
            predicted_ys = loadedpipe.predict(triplesList)  #get predictions
            sentimentList = predicted_ys.tolist()   #convert predictions to list
            count = 0
            totalTweetsProcessed += len(data) 
            for dict in data:
                keydropped = dict.pop("tagged_tweet_triples",None)  #stored as variable in order to supress print to screen
                dict["sentiment_score"] = sentimentList[count]   #append prediction to dictionary
                count += 1
            helper.dumpJSONtoFile(outFilePath + file,data)   #dump live tweets with classifer predictions added to json
            filesProcessed +=1
            print "Total files remaining = " + str(totalFiles - filesProcessed)
        except Exception as error:
            fileErrors +=1
            os.rename(inFilePath + file,inFilePath +'errors/'+ file)
            errorFile.write("Error Processing Tweet file for sentiment classification. File name: " + file + " With error: " + str(error) + '\n')
            continue
        
        print("Get Sentiment time--- %s seconds ---" % (time.time() - st_getsentiment_time))
        print("Total elapsed time--- %s seconds ---" % (time.time() - start_time))
        
        #delete current file from inFile directory, tweets have been processes succesfully and moved to next step, or written to error folder
        helper.deleteFilesInList(inFilePath,[file])
    
    print str(filesProcessed) + " files processed with error files = " + str(fileErrors)
    print str(totalTweetsProcessed) + " tweets processed."
    print("completed in--- %s seconds ---" % (time.time() - start_time))
    
    errorFile.close()

def prepTweetsDb():
    start_time = time.time()
    inFilePath = "5-ClassifiedTweets/"
    outFilePath = "6-TweetsReadyForDB/"
    files = helper.getListOfFiles(inFilePath)
    totalTweetsProcessed = 0
    totalTweetErrors = 0
    
    totalFiles = len(files)
    filesProcessed = 0
    fileErrors = 0
    
    errorFile = open(inFilePath + "errors/errorFile.log","a")
    
    listOfErrorDicts = []
    
    print str(totalFiles) + " total tweet files will be prepped for DB starting now...."        
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
            os.rename(inFilePath + file,inFilePath +'errors/'+ file)
            errorFile.write("Error Processing Tweet file for DB Prep. File name: " + file + " With error: " + str(error) + '\n')
            continue
        
        print("Current file prep time--- %s seconds ---" % (time.time() - file_time))

        print("Total elapsed time--- %s seconds ---" % (time.time() - start_time))

        #delete current file from inFile directory, tweets have been processes succesfully and moved to next step, or written to error folder
        helper.deleteFilesInList(inFilePath,[file])
        
    print str(filesProcessed) + " files processed with error files = " + str(fileErrors)
    print str(totalTweetsProcessed) + " tweets processed."
    print("completed in--- %s seconds ---" % (time.time() - start_time))
    
def batchLoadTweets():
    '''Provided a directory path containing full processed/classified tweets.'''
    start_time = time.time()
    #inFilePath = "5-TweetsReadyForDB/temp/"
    inFilePath = "6-TweetsReadyForDB/"
    files = helper.getListOfFiles(inFilePath)
    totalTweetsProcessed = 0
    totalTweetErrors = 0
    
    totalFiles = len(files)
    filesCompleted = 0
    fileErrors = 0
    
    errorFile = open(inFilePath + "errors/errorFile.log","a")
    
    listOfErrorDicts = []
    
    #db setup
    s = db.Tweet()
    
    print str(totalFiles) + " total tweet files will be loaded to db starting now...."        
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
                    s = db.Tweet()
                    totalTweetErrors+=1
                    dict['ERROR']='Error finding metar report via pipe.getTweetMetarReport, perhaps none was available for station/time combo. Error: ' + str(error) + '. Original file = ' + file.split('/')[-1]
                    listOfErrorDicts.append(dict)                    
                    continue
            filesCompleted += 1
            if (totalTweetsInFileProcessed % 100) == 0:
                print str(totalTweetsInFileProcessed) + " tweets loaded for current file of total tweets = " + str(totalTweetsInFile)
        except Exception as error:
            fileErrors +=1
            os.rename(inFilePath + file,inFilePath +'errors/'+ file)
            errorFile.write("Error Processing Tweet file for DB Prep. File name: " + file + " With error: " + str(error) + '\n')
            continue
        print str(filesCompleted) + " files loaded of " + str(totalFiles) + ". Current file = " + file
        print str(totalTweetsProcessed) + " tweets loaded into DB. With total tweet errors = " + str(totalTweetErrors)
        print("Current file prep time--- %s seconds ---" % (time.time() - file_time))

        #print("Total elapsed time--- %s minutes ---" % (((totalFiles - (filesCompleted+fileErrors))*(time.time() - start_time))/60.)
        print "Total files remaining = " + str(totalFiles - (filesCompleted+fileErrors))
        print "Estimated time remaining in minutes = " + str(((totalFiles - (filesCompleted+fileErrors))*(time.time() - file_time))/60.)

        #Dump dictionary errors and log details    
        dumpErrorListOfDicts(inFilePath,listOfErrorDicts)
        listOfErrorDicts = []

        #delete current file from inFile directory, tweets have been processes succesfully and moved to next step, or written to error folder
        helper.deleteFilesInList(inFilePath,[file])
    
    
    print str(filesCompleted) + " files processed with error files = " + str(fileErrors)
    print str(totalTweetsProcessed) + " tweets loaded into DB. With total tweet errors = " + str(totalTweetErrors)
    print("Total completion time in minutes--- %s minutes ---" % ((time.time() - start_time)/60.))   



def main():
    start_time = time.time()
    
    print ".............Getting Weather.............."
    getWx()
    print "...............Getting NLP Triples and Topics.................."
    getTriplesAndTopics()
    print "..................Classifying.............."
    getClassifications()
    print "................PREPPING FOR DB.............."
    prepTweetsDb()
    print "..............BATCH LOADING TO DB............"
    batchLoadTweets()
    
    print("Total completion time in minutes--- %s minutes ---" % ((time.time() - start_time)/60.))  
    print "DONE!!!"  

