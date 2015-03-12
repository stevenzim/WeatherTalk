import json
from os import listdir
from os.path import isfile, join
import os as os

#load json
def loadJSONfromFile(fileName):	
	'''Loads JSON data into list.  Returns a list of dictionaries in [{},{}...{}] format
	fileName is relative to directory where Python is running.
	usage: myListOfDicts = loadJSONfromFile("FileName") '''
	return json.loads(open(fileName).read())

#pretty print json
def dumpJSONtoFile(fileName , dataToDump):
    '''BORROWED FROM GROUP PROJECT: Dumps JSON data from dictionaries in list into output file. This data is pretty printed
        for readability. fileName is relative to directory where Python is running.
        dataToDump should be in [{},{}...{}] format
        usage: dumpJSONtoFile("FileName", myListOfDicts)'''
    with open(fileName, 'w') as outfile:
        json.dump(dataToDump, outfile ,sort_keys=True, indent=4, separators=(',', ': '))
        

def getListOfFiles(path):
    '''A modification of this post: 
    http://stackoverflow.com/questions/3207219/how-to-list-all-files-of-a-directory-in-python
    Input = path to directory containing files you want to list
    Returns a a list of all files in path
    '''
    listOfFiles = [ file for file in listdir(path) if isfile(join(path,file)) ]
    return listOfFiles
    #check if open
    # test = True
    # for file in listOfFiles:
        # try:
            # testOpen = open(file,'w')
            # testOpen.close()
        # except:
            # print "File still open"
            # test = False
        
    # if test:        
        # return listOfFiles
    # else:
        # return None

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
