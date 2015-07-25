from wxtalk.externals.tweetNLP import cmuTweetTagger as tweetNLPtagger

import json
import csv
from datetime import datetime
from os import listdir
from os.path import isfile, join
import os as os
from time import time
import numpy as np

from sklearn.metrics import classification_report
from sklearn.metrics import f1_score

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
def evaluateResults(y_expected,y_predicted,y_probs = None,prob_thresh = .95):
    '''Get evaluation results e.g. Precision, Recall and F1 scores
        If probabilities for ys is provided then only return classification report
        with prediction probabilities greater than threshold default 95%'''
    if y_probs == None:
        return classification_report(y_expected,y_predicted)
    #below usefule for when you want to only evaluate based on predictions with probability > threshold
    #NOTE: does not have test YET
    thresh_expected = []
    thresh_predicted = []
    for expect, predict, prob in zip(y_expected,y_predicted,y_probs):
        if prob.max() > prob_thresh:
            thresh_expected.append(expect)
            thresh_predicted.append(predict)
        else:
            continue
    return classification_report(np.asarray(thresh_expected),np.asarray(thresh_predicted))

      
		
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
def getDateTimeStamp(ansiFormat = False):
    '''
    returns a string formatted datetime stamp useful for error files
    ansiFormat True is useful for db calls
    ansiFormat False is useful for file naming
    '''
    if ansiFormat:
        return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    else:
        return datetime.utcnow().strftime('%Y-%m-%d-%H%M')
  
    
# Run TweetNLP on list of dictionaries
def extractTweetNLPtriples(JSONfilePathOrListOfDicts,outputJSONfile = None):
    '''Loads json file to list --> creates list of tweets for all dictionaries in list
    Then runs the TweetNLP tagger (from Carnegie Mellon) on list of tweets
    Results of TweetNLP tagger are then added to appropriate dictionary which is dumped to new file
    This is done as independent task to allow jvm to process a batch of tweets
    rather than restarting for each individual tweet
    usage: tweetPreprocessedKeyVals("resources/preTweetNLP.json","resources/postTweetNLP.json")'''
    listOfDicts = []
    if type(JSONfilePathOrListOfDicts) == type(''):
        listOfDicts = loadJSONfromFile(JSONfilePathOrListOfDicts)
    elif type(JSONfilePathOrListOfDicts) == type([]):
        try:
            listOfDicts = JSONfilePathOrListOfDicts
        except:
            raise Exception('No tweets in list provided or incorrect data type provided')
    else:
        raise Exception('You must provide a file path to json file containing tweets OR a list of tweet dictionaries')
    
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
    
    #dump list of dictionaries with triples to output folder OR return list of dictionaries
    if outputJSONfile == None:
        return listOfDicts
    else:
        dumpJSONtoFile(outputJSONfile, listOfDicts)

#A toy example to identify topics.  E.g. identify occurences of Obama in a tweet    
def addStringTestTopic(dictionary,keyToSearch,stringToTest,keyNameToAdd):
    '''Provided a dictionary, desired string to look for,key to search for string and key name to add
    test for occurance of string in lower case format and put result into new key.  Returns an updated dictionary'''
    stringToSearch = dictionary[keyToSearch].lower()
    stringToTest = stringToTest.lower()
    dictionary[keyNameToAdd] = stringToTest in stringToSearch
    return dictionary
     
     
#get project path for current Python project
def getProjectPath():
    '''
    useful for returning full project path. With project path, one can then easily join relative paths to project path.
    This only works assuming project is set up in python path correctly
    This code is a modfied version found at http://stackoverflow.com/questions/1489599/how-do-i-find-out-my-python-path-using-python
    '''
    try:
        user_paths = os.environ['PYTHONPATH'].split(os.pathsep)
        return user_paths[1]
    except KeyError:
        user_paths = []    
     
#converts a csv file with header to a list of dictionaries, very useful for loading this type of data into database
def csvToDicts(filepath):
    '''converts a csv file with header to a list of dictionaries, very useful for loading this type of data into database
    simply pass in the full path to csv file'''
    listOfDicts = [] 
    keys = ''    
    with open(filepath, mode='r') as infile:
        keys = infile.readline()
        keys = keys.replace("\r\n","")
        keys = keys.split(',')
        reader = csv.reader(infile)
        for rows in reader:
            currentdict = {}
            idx = 0
            for key in keys:
                currentdict[key] = rows[idx]
                idx +=1
            listOfDicts.append(currentdict)
    return listOfDicts
    
    
#convert dict to format for sql insertion
def keysValsToSQL(dict):
    '''Very useful for situation when dictionary has key names that match the column names in database'''
    #inspired by http://stackoverflow.com/questions/29461933/insert-python-dictionary-using-psycopg2
    #convert keys to column names and then create string
    columns = dict.keys()
    columns_str = ", ".join(columns)
    #convert values to column names and then create string
    values = [dict[x] for x in columns]
    values_str_list = [str(value) for value in values]
    values_str = "\',\'".join(values_str_list)
    return columns_str, values_str

def loadLexicon(lexicon,gramType = None):
    '''Load desired lexicon based on input values e.g. lexicon = 'BingLiu and gramType = 'unigram' '''
    #TODO: Throw exception error if GramType None and lexicon requires unigram or bigram

     ###manual lexicon file details
    #Bing Liu lexicon path and files
    BingLiuPath = getProjectPath() +  '/wxtalk/resources/lexicons/BingLiu/'       
    BingLiufile = {'unigram': BingLiuPath + 'BingLiu.json'}
    #MPQA lexicon path and files
    MPQAPath = getProjectPath() +  '/wxtalk/resources/lexicons/MPQA/'       
    MPQAfile = {'unigram': MPQAPath + 'MPQA.json'}
    #NRCemotion lexicon path and files
    NRCemotionPath = getProjectPath() +  '/wxtalk/resources/lexicons/NRC-emotion/'       
    NRCemotionfile = {'unigram': NRCemotionPath + 'NRC-emotion.json'}

    ###automatic lexicon file details
    #NRC 140 lexicon path and files
    NRC140Path = getProjectPath() +  '/wxtalk/resources/lexicons/NRC-Sent140/'       
    NRC140files = {'unigram': NRC140Path + 'unigrams140.json',\
                        'bigram': NRC140Path + 'bigrams140.json',\
                        'pairs': NRC140Path + 'pairs140.json'}
    #NRC Hashtag lexicon path and files
    NRCHashPath = getProjectPath() +  '/wxtalk/resources/lexicons/NRC-Hash/'       
    NRCHashfiles = {'unigram': NRCHashPath + 'unigramsHash.json',\
                        'bigram': NRCHashPath + 'bigramsHash.json',\
                        'pairs': NRCHashPath + 'pairsHash.json'} 
    
  
    
    #CMU cluster lexicon path/file
    CMUclusterLexFile = getProjectPath() + '/wxtalk/resources/lexicons/CMU/CMU-cluster-lexicon.json'
    
    #KLUE Emoticon path and file
    KLUEemoticonFile = getProjectPath() +  '/wxtalk/resources/lexicons/KLUE/KLUEemoticon.json'       

    #KLUE acronym path and file
    KLUEacronymFile = getProjectPath() +  '/wxtalk/resources/lexicons/KLUE/KLUEemoticon.json' 
    
    #KLUE Combined Emoticon/Acronym path and file
    KLUEemotiANDacroFile = getProjectPath() +  '/wxtalk/resources/lexicons/KLUE/KLUEemotiANDacro.json'       

    #KLUE AFINN path and file
    KLUEafinnFile = getProjectPath() +  '/wxtalk/resources/lexicons/KLUE/AFINN.json'    

    #SentiWordNet path and file
    SentiWordNetFile = getProjectPath() +  '/wxtalk/resources/lexicons/SentiWordNet/SentiWord.json'  

    #load appropriate file
    if lexicon == 'BingLiu':
        lexicon = loadJSONfromFile(BingLiufile[gramType])
    elif lexicon == 'MPQA':
        lexicon = loadJSONfromFile(MPQAfile[gramType]) 
    elif lexicon == 'NRCemotion':
        lexicon = loadJSONfromFile(NRCemotionfile[gramType]) 
    elif lexicon == 'NRC140':
        lexicon = loadJSONfromFile(NRC140files[gramType])
    elif lexicon == 'NRCHash':
        lexicon = loadJSONfromFile(NRCHashfiles[gramType]) 
    elif lexicon == 'cmu-cluster-lex':
        lexicon = loadJSONfromFile(CMUclusterLexFile)
    elif lexicon == 'emoticon':
        lexicon = loadJSONfromFile(KLUEemoticonFile )
    elif lexicon == 'acronym':
        lexicon = loadJSONfromFile(KLUEacronymFile )
    elif lexicon == 'klue-both':
        lexicon = loadJSONfromFile(KLUEemotiANDacroFile )
    elif lexicon == 'klue-afinn':
        lexicon = loadJSONfromFile(KLUEafinnFile )
    elif lexicon == 'SentiWord':
        lexicon = loadJSONfromFile(SentiWordNetFile )
    elif type(lexicon) == type({}):
        #this case put here to handle situation when dict is already loaded (e.g. when loading a pickle file)
        lexicon = lexicon
    else:
        raise TypeError("You need to provide a correct lexicon and or gramType") 
        
    return lexicon
