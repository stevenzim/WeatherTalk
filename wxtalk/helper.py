from wxtalk.externals.tweetNLP import cmuTweetTagger as tweetNLPtagger

import json
from datetime import datetime
from os import listdir
from os.path import isfile, join
import os as os
from time import time

from sklearn.metrics import classification_report


#load json
def loadJSONfromFile(fileName):	
	'''Loads JSON data into list.  Returns a list of dictionaries in [{},{}...{}] format
	fileName is relative to directory where Python is running.
	usage: myListOfDicts = loadJSONfromFile("FileName") '''
	return json.loads(open(fileName).read())

#pretty print json
def dumpJSONtoFile(fileName , dataToDump):
	'''Dumps JSON data from dictionaries in list into output file. This data is pretty printed
		for readability. fileName is relative to directory where Python is running.
		dataToDump should be in [{},{}...{}] format
		usage: dumpJSONtoFile("FileName", myListOfDicts)'''
	with open(fileName, 'w') as outfile:
		json.dump(dataToDump, outfile ,sort_keys=True, indent=4, separators=(',', ': '))

#produce model metrics		
def evaluateResults(y_expected,y_predicted):
    '''Get evaluation results e.g. Precision, Recall and F1 scores'''
    return classification_report(y_expected,y_predicted)
		
#drop keys and vals from list of dicts based on list of keys to drop, default is none		
def dropKeysVals(listOfDicts, keysToDrop = []):
    '''Remove specified Keys and Values from dictionaries stored in list based 
    on provided list of keysToDrop'''
    #TODO: Perhaps there is a map reduce fucntion that could do this better???
    #       similar to map over in clojure
    #TODO: Perhaps it is less confusing to base it on keys to keep (i.e. features to keep)
    #       vs. keys to drop (i.e. features to drop)
    #TODO: Determine how to pass in list of args to transformers, 
    #       which will then be passed to this function
    if type(keysToDrop) != type([]):
        raise TypeError
        #raise ValueError('keysToDrop must be in a list!')
    #no keys to drop so return full list of dicts
    if len(keysToDrop) == 0:
        return listOfDicts
    #iterate over entire list of dicts --> for each dict iterate over list of keys
    # to drop and drop key --> then add updated dictionary to return list 
    returnList = []
    for dictionary in listOfDicts:
        for keyName in keysToDrop:
            try:
                dictionary.pop(keyName)
            except:
                raise ValueError('invalid key name in list!')
                continue
        returnList.append(dictionary)
    return returnList
    
#list all files in a path    
def getListOfFiles(path):
    '''A modification of this post: 
    http://stackoverflow.com/questions/3207219/how-to-list-all-files-of-a-directory-in-python
    Input = path to directory containing files you want to list
    Returns a a list of all files in path
    '''
    listOfFiles = [ file for file in listdir(path) if isfile(join(path,file)) ]
    return listOfFiles

#delete files - given a list of files and directory containing files
def deleteFilesInList(dirName,listOfFiles):
    '''
    Input = directory name AND list of files in directory to delete
    '''
    for file in listOfFiles:
        path = dirName + '/' + file
        try:
            os.remove(path)
        except:
            continue


#get date timestamp  string          
def getDateTimeStamp():
    '''
    returns a string formatted datetime stamp useful for error files
    '''
    return datetime.utcnow().strftime('%Y-%m-%d-%H%M')
    
    
# Run TweetNLP on list of dictionaries
def extractTweetNLPtriples(inputJSONfile,outputJSONfile):
    '''Loads json file to list --> creates list of tweets for all dictionaries in list
    Then runs the TweetNLP tagger (from Carnegie Mellon) on list of tweets
    Results of TweetNLP tagger are then added to appropriate dictionary which is dumped to new file
    This is done as independent task to allow jvm to process a batch of tweets
    rather than restarting for each individual tweet
    usage: tweetPreprocessedKeyVals("resources/preTweetNLP.json","resources/postTweetNLP.json")'''
    listOfDicts = loadJSONfromFile(inputJSONfile)
    listOfTweets = []
    for dict in listOfDicts:
        tweet = dict["text"]
        tweet = tweet.replace("\r","\n")  #The \r escape character must be replaced with\n, \
                                           #or else TweetNLP splits tweet on this character thus outputting triples for two seperate
                                            #tweets rather than one
        listOfTweets.append(tweet)
    
    print "Running TweetNLP On: " + str(len(listOfTweets)) + " tweets"
    t0 = time()
    
    tweetNLPtriples = tweetNLPtagger.runtagger_parse(listOfTweets)  #send tweets to tagger which returns triples
    
    print "Done with NLP extractor"
    print(str(len(tweetNLPtriples)) + " tweets processed in %0.3fs" % (time() - t0))
    
    #error handling, if tagger returns a different number of triples than tweets passed in, then ther is a problem
    if len(tweetNLPtriples) != len(listOfTweets):
        raise Exception("Total number of triples returned from tweetNLP does not match number of tweets passed in! Review file in: " + outputJSONfile)
	
	#If there were no errors, then attach the triple to its corresponding dictionary
    for idxAndTriple in enumerate(tweetNLPtriples):
	    idx = idxAndTriple[0]
	    triple = idxAndTriple[1]
	    listOfDicts[idx]['tagged_tweet_triples'] = triple
    
    #dump list of dictionaries with triples to output folder
    dumpJSONtoFile(outputJSONfile, listOfDicts)
