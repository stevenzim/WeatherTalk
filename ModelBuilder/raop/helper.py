import json
import raop.preprocess.preprocess as preprocess

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