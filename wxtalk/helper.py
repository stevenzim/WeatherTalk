import json
from datetime import datetime
from os import listdir
from os.path import isfile, join
import os as os
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
            
def getDateTimeStamp():
    '''
    returns a string formatted datetime stamp useful for error files
    '''
    return datetime.utcnow().strftime('%Y-%m-%d-%H%M')
