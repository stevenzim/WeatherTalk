from wxtalk import helper, pipeline
from wxtalk.db import dbfuncs as db
from wxtalk.model import transformers as tran
from wxtalk.model import (predictors,ensemblers)

import time
import string
import os

import sklearn.externals.joblib as joblib




def dumpErrorListOfDicts(filePath,listOfErrorDicts,description,origFileName):
    '''Dumps dictionaries with errors to json file. '''
    if len(listOfErrorDicts) > 0:
        helper.dumpJSONtoFile(filePath + 'errors/error-dicts-' + description + origFileName,listOfErrorDicts)        


def organizeTweets():
'''
-useful for disk management and shaving down size of corpus
-takes a set files containing tweets in JSON and combines them into larger files (e.g. >15K tweets per file)
-If tweet date before 27APR2015(date of API change) then only take 2/9 and dump remainder to other folder to process later if time permits 
'''
    start_time = time.time()
    inFilePath = "1-CleanedTweets/2015-March/"
    outFilePath = "2-OrganizedTweets/March/"
    files = helper.getListOfFiles(inFilePath)
    files.sort()  #put oldest first
    totalTweetsProcessed = 0
    totalTweetErrors = 0
    tweetsHeldOut = 0
    
    totalFiles = len(files)
    filesProcessed = 0
    fileErrors = 0
    
    errorFile = open(inFilePath + "errors/errorFile.log","a")
    
    listOfErrorDicts = []
    listOfFilesToDelete = []
    
    tweetsToSetAside = []      #random subset that will be stored for later processing if time 2 of every 9 will be held out for now
    tweetsToProcess = []
    firstFileName = None
    
    print str(totalFiles) + " total tweet files will be organized...."        
    for file in files:
        file_time = time.time()
        if firstFileName == None:
            firstFileName = file
        try:
            print
            print
            print file + " is being organized."
            data = helper.loadJSONfromFile(inFilePath +file)  
            totalTweetsProcessed += len(data) 
                        
            #test if tweet occured before Twitter API change on Mon Apr 27 17:41:29 2015
            if int(data[0]["timestamp_ms"]) < 1430156489629:
                count = 0
                for dict in data:
                    if (((count % 9) != 4) and ((count % 9) != 8)):
                        tweetsToSetAside.append(dict)
                    else:
                        tweetsToProcess.append(dict)
                    count +=1
                if len(tweetsToSetAside) > 0:
                    helper.dumpJSONtoFile("2-OrganizedTweets/setAsideBeforeAPI/" + file,tweetsToSetAside) 
                    tweetsHeldOut += len(tweetsToSetAside)
                    tweetsToSetAside = []              
            else:
                tweetsToProcess.extend(data)
            filesProcessed +=1
            print "Total files remaining = " + str(totalFiles - filesProcessed)
            
            listOfFilesToDelete.append(file)
        except Exception as error:
            fileErrors +=1
            os.rename(inFilePath + file,inFilePath +'errors/'+ file)
            errorFile.write("Error organizing Tweet file for DB Prep. File name: " + file + " With error: " + str(error) + '\n')
            continue
        
        print("Current file prep time--- %s seconds ---" % (time.time() - file_time))

        print("Total elapsed time--- %s seconds ---" % (time.time() - start_time))

        #delete current files from inFile directory in the list of Files to delete
        if len(tweetsToProcess) > 15000:
            helper.dumpJSONtoFile(outFilePath + firstFileName,tweetsToProcess)
            tweetsToProcess = []
            firstFileName = None          
            helper.deleteFilesInList(inFilePath,listOfFilesToDelete)
            listOfFilesToDelete = []

    #final file dump and deletes
    if len(tweetsToProcess) > 0:
        helper.dumpJSONtoFile(outFilePath + firstFileName,tweetsToProcess)     
        helper.deleteFilesInList(inFilePath,listOfFilesToDelete)
              
    print str(filesProcessed) + " files processed with error files = " + str(fileErrors)
    print str(totalTweetsProcessed) + " tweets processed."
    print("completed in--- %s seconds ---" % (time.time() - start_time))
    errorFile.write("Total tweets=," + str(totalTweetsProcessed) + ",Total tweets errors=," + str(totalTweetErrors) + ",Total tweets held out=," + str(tweetsHeldOut) +\
                      ",Total files processed =," + str(filesProcessed) + ",Total file errors=," + str(fileErrors) + "\n")    
    errorFile.close()
        

def getWx(monthName):
    '''take a set of json files of tweets and load them with uids of most recent wx report and nearest station'''
    start_time = time.time()
    inFilePath = "2-OrganizedTweets/"+ monthName + "/"
    outFilePath = "3-TweetsWithWx/"+ monthName + "/"
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
        listOfErrorDicts = []
        tweetsWithMetar = []
        tweetsWithClimate = []
        toManyErrors = False
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

        for dict in tweetListWithWxStations: 
            try:
                tweetsWithMetar.append(pipeline.getTweetMetarReport(dict))
            except Exception as error:
                totalTweetErrors += 1
                dict['ERROR']='Error finding metar report via pipe.getTweetMetarReport, perhaps none was available for station/time combo. Error:' + str(error) + '. Original file = ' + file.split('/')[-1]
                listOfErrorDicts.append(dict)
                #helper.dumpJSONtoFile(inFilePath + 'errors/' + str(totalTweetErrors) + "-" + file,dict)
                #errorFile.write("ERROR: " + str(error) + " Error: getTweetMetarReport for file: " + file + " and tweet ID: " + str(dict["id"]) + "\n")
                continue
            
            #analysis of this step indicates if many tweets can't find metar, then it wasn't loaded into db, therefore we want to dump it to error file and get onto next file
            if len(listOfErrorDicts) > 100 and len(tweetsWithMetar) < 2:
                helper.dumpJSONtoFile(inFilePath + 'errors/metar-missing-' + file,tweetListWithWxStations)   
                toManyErrors = True
                break
        
        #test if there are many metar errors, if so, we want to go onto next file    
        if toManyErrors == True:
            helper.deleteFilesInList(inFilePath,[file])
            continue
                     
        print("Get Metar Report time--- %s seconds ---" % (time.time() - st_getmetarreport_time))


        #link tweet to climate report
        #   This only links tweet occuring in local time window of report (i.e. 24 hours).  That is if the tweet occurs 1 minute after start time of new report
        # Then the uid of the new report is linked to tweet.  This is not ideal, but it is simple, can be further updated in future work.  In analysis, one should consider
        # filtering out tweets where climate delta time is small as the report is representative of only a short window of time for the tweet
        # That said, concern is low, because most tweets do not happen in the couple of hours after start time of report as this is start of local day when most people are sleeping
        # and tweet rates are low
        st_getclimatereport_time = time.time()

        for dict in tweetsWithMetar: 
            try:
                tweetsWithClimate.append(pipeline.getTweetClimateReport(dict))
            except Exception as error:
                totalTweetErrors += 1
                dict['ERROR']='Error finding climate report via pipe.getTweetClimateReport. Error:' + str(error) + '. Original file = ' + file.split('/')[-1]
                listOfErrorDicts.append(dict)
                continue
        if len(tweetsWithClimate) > 0:
            helper.dumpJSONtoFile(outFilePath + file,tweetsWithClimate)
        print("Get Climate Report time--- %s seconds ---" % (time.time() - st_getclimatereport_time))
        print
        print("Total elapsed time--- %s seconds ---" % (time.time() - start_time))
        
        
        print "Estimated time remaining in minutes = " + str(((totalFiles - (filesProcessed+fileErrors))*(time.time() - st_getstation_time))/60.)

        #Dump any remaining errors and log details of current processing to error file      
        dumpErrorListOfDicts(inFilePath,listOfErrorDicts,"get-wx-",file)

            
        #delete current file from inFile directory, tweets have been processes succesfully and moved to next step, or written to error folder
        helper.deleteFilesInList(inFilePath,[file])
    
    print str(filesProcessed) + " files processed with error files = " + str(fileErrors)
    print str(totalTweetsProcessed) + " tweets processed with tweet errors = " + str(totalTweetErrors)  
    print("completed in--- %s seconds ---" % (time.time() - start_time))
    

    errorFile.write("Total tweets=," + str(totalTweetsProcessed) + ",Total tweets errors=," + str(totalTweetErrors) +\
                      ",Total files processed =," + str(filesProcessed) + ",Total file errors=," + str(fileErrors) + "\n")
    errorFile.close()
    
def classifyTweets(monthName):
    '''Input is a tweet with metar/climate report ids
    Output is a tweet with classification details for each model and the ensemble model.  
    For sentiment classification, probabilities are provided in addition to discrete classes
    For weather topic classication, only a discrete boolean score is provided'''
    start_time = time.time()
    inFilePath = "3-TweetsWithWx/"+ monthName + "/"
    outFilePath = "4-ClassifiedTweets/"+ monthName + "/"
    files = helper.getListOfFiles(inFilePath)
    totalTweetsProcessed = 0
    totalTweetErrors = 0
    
    totalFiles = len(files)
    filesProcessed = 0
    fileErrors = 0
    
    errorFile = open(inFilePath + "errors/errorFile.log","a")
    
    listOfErrorDicts = []
    listOfCompletedFiles = []
    
    modelList = [predictors.NRCmodelMetaData,\
                predictors.KLUEmodelMetaData,\
                predictors.GUMLTLTmodelMetaData,\
                predictors.wxFullFeats]
    
    print str(totalFiles) + " total tweet files will be processed for tweet sentiment/weather classification...."
    
    for file in files:
        clf_tweets_time = time.time()
        classifiedFilePath = outFilePath + file
        try:
            #produce model predictions and output to predicited tweeets file
            origTweets = helper.loadJSONfromFile(inFilePath + file)
            print "Classifying sentiment and weather for file = " + file + " which contains " + str(len(origTweets)) + " Tweets."
            modelResults = predictors.makePredictions(modelList,origTweets)
            fullyClassifiedTweets = ensemblers.compileEnsemble([ensemblers.webisEnsemble],modelResults)
            fullyClassifiedTweets = helper.dropKeysVals(fullyClassifiedTweets, ['s1_proba','s2_proba','s3_proba','w1_proba'])  #remove model probabilistic data
            helper.dumpJSONtoFile(classifiedFilePath,fullyClassifiedTweets)
            filesProcessed +=1
            totalTweetsProcessed += len(fullyClassifiedTweets)
            print "Just classiified " + str(len(fullyClassifiedTweets)) + ".  Total tweets classified = " + str(totalTweetsProcessed)
            print "Total files remaining = " + str(totalFiles - filesProcessed)
        except Exception as error:
            #if there is an error classifying tweets, then dump file to error folder 
            print error
            fileErrors +=1
            os.rename(inFilePath + file,inFilePath +'errors/'+ file)
            errorFile.write("Error for current list of tweets passed to pipe.classifyTweets for file: " + file + " ERROR: " + str(error))  + '\n'
            continue
            print(file + " total classification time--- %s seconds ---" % (time.time() - clf_tweets_time))
        print "Total elapsed time in minutes = " + str((time.time() - start_time)/60.)
        print "Estimated time remaining in minutes = " + str(((totalFiles - (filesProcessed+fileErrors))*(time.time() - clf_tweets_time))/60.)
        print
        print
        #delete current file from inFile directory, tweets have been classified succesfully and moved to next step, or written to error folder
        helper.deleteFilesInList(inFilePath,[file])


def loadTweetsToDB(monthName):
    '''Input is a tweet with classifications
    Output is same tweet to raw file repository
    Processing steps are:
    1 - load all file names
    2 - for each file make a temp copy and do the following:
        a) get topic booleans based on occurence of text string (this is purely for fun analysis)
        b) rename fields (e.g. e1_s1_discrete --> sentiment_class)
        c) remove fields that will not be loaded into db (e.g. text/username)
        d) load into db
    3 - If an error occurs, dump to appropriate error folder, else move original file to final storage folder
    '''
    start_time = time.time()
    inFilePath = "4-ClassifiedTweets/"+ monthName + "/"
    outFilePath = "5-TweetsLoadedToDB/"+ monthName + "/"
    files = helper.getListOfFiles(inFilePath)
    totalTweetsProcessed = 0
    totalTweetErrors = 0
    
    totalFiles = len(files)
    filesProcessed = 0
    fileErrors = 0
    
    errorFile = open(inFilePath + "errors/errorFile.log","a")
    
    listOfErrorDicts = []
    listOfCompletedFiles = []
    
    #establish db connection for tweet loading
    s = db.Tweet()
    
    print str(totalFiles) + " total tweet files will be processed for loading into DB...."
    
    for file in files:
        db_loading_time = time.time()
        finalFilePath = outFilePath + file  #path to final storage folder for tweets
        try:
            #produce model predictions and output to predicited tweeets file
            origTweets = helper.loadJSONfromFile(inFilePath + file)
            print "Processing and loading tweets to DB for file = " + file + " which contains " + str(len(origTweets)) + " Tweets."
            #
            tweetsToSave = []
            tweetsToLoadToDB = [] 
            for tweet in origTweets:
                tweetsToSave.append(tweet.copy()) #keep original classified tweet
                #add in boolean topics based on occurence of word in text (simple topic analyzer only for fun)
                tweet = helper.addStringTestTopic(tweet,'text','obama','topic_obama')
                tweet = helper.addStringTestTopic(tweet,'text','adidas','topic_adidas')
                tweet = helper.addStringTestTopic(tweet,'text','nike','topic_nike')
                tweet = helper.addStringTestTopic(tweet,'text','boeing','topic_boeing')
                tweet = helper.addStringTestTopic(tweet,'text','microsoft','topic_microsoft')
                tweet = helper.addStringTestTopic(tweet,'text','tableau','topic_tableau')
                tweet = helper.addStringTestTopic(tweet,'text','verizon','topic_verizon')
                tweet = helper.addStringTestTopic(tweet,'text','apple','topic_apple')
                tweet = helper.addStringTestTopic(tweet,'text','samsung','topic_samsung')
                tweet = helper.addStringTestTopic(tweet,'text','wal-mart','topic_walmart')
                
                #add in desired names of fields (these are same fields in DB)
                tweet['sentiment_class'] = tweet['ens_s1_discrete']
                tweet['sentiment_probability'] = tweet['ens_s1_proba']
                tweet['weather_class'] = tweet['w1_discrete']
                tweet['user_id'] = tweet['user']['id']
                tweet['coordinates'] = str(tuple(tweet['coordinates']['coordinates']))
                
                #remove fields that will not be loaded into db
                keysToDrop = ["in_reply_to_status_id","in_reply_to_user_id","lang","metar_report","timestamp_ms","user","text",\
                                'ens_s1_discrete','ens_s1_proba','s1_discrete','s2_discrete','s3_discrete','w1_discrete',\
                                'quoted_status','quoted_status_id','quoted_status_id_str','scopes']

                #pop the list of keys, these key names are not valid columns in db.
                for key in keysToDrop:
                    temp = tweet.pop(key,None)  #stored as temp variable in order to supress print to screen
                
                #load tweet into db
                s.loadTweet(tweet)
                
                tweetsToLoadToDB.append(tweet) #temp file to view
              
            helper.dumpJSONtoFile(inFilePath + 'errors/loadedTemp.json',tweetsToLoadToDB)  #only keep this as temp file (stored in errror folder)
            
            helper.dumpJSONtoFile(finalFilePath,tweetsToSave)  #dump original tweets
            filesProcessed +=1
            totalTweetsProcessed += len(origTweets)
            print "Just loaded " + str(len(origTweets)) + ".  Total tweets loaded to DB = " + str(totalTweetsProcessed)
            print "Total files remaining = " + str(totalFiles - filesProcessed)
        except Exception as error:
            #if there is an error processing and loading tweets to DB, then dump file to error folder 
            print error
            fileErrors +=1
            os.rename(inFilePath + file,inFilePath +'errors/'+ file)
            errorFile.write("Error for current list of tweets passed to pipe.loadTweetsToDB for file: " + file + " ERROR: " + str(error))  + '\n'
            continue
            print(file + " total loading to DB time--- %s seconds ---" % (time.time() - db_loading_time))
        print "Total elapsed time in minutes = " + str((time.time() - start_time)/60.)
        print "Estimated time remaining in minutes = " + str(((totalFiles - (filesProcessed+fileErrors))*(time.time() - db_loading_time))/60.)
        print
        print
        #delete current file from inFile directory, tweets have been processed and loaded succesfully to DB and moved to final storage folder, or written to error folder
        helper.deleteFilesInList(inFilePath,[file])




def main():
    start_time = time.time()
    
    print ".............Getting Weather.............."
    getWx()
    print "...............Getting NLP Triples and Topics.................."
    getTriplesAndTopics()
#    print "..................Classifying.............."
#    getClassifications()
#    print "................PREPPING FOR DB.............."
#    prepTweetsDb()
#    print "..............BATCH LOADING TO DB............"
#    batchLoadTweets()
    
    print("Total completion time in minutes--- %s minutes ---" % ((time.time() - start_time)/60.))  
    print "DONE!!!"  

