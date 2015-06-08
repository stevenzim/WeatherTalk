import json
import twxeety.preprocess.preprocess as preprocess
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
