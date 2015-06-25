import flatdict
from wxtalk import helper
import os
import os.path

#usage: from wxtalk.resources.scripts import getFlatClimateKeys as fl


#files = helper.getListOfFiles(".")
count = 0
filecount = 0
outDict = {}




files = []
for dirpath, dirnames, filenames in os.walk("."):
    for filename in [f for f in filenames if f.endswith(".json")]:
        files.append( os.path.join(dirpath, filename))



for file in files:
    #try:
    climDict = helper.loadJSONfromFile(file)
    flatWxDict = flatdict.FlatDict(climDict[climDict.keys()[0]])
    keysList = flatWxDict.keys()
    for key in keysList:

        if key.replace(':','_').replace(' ','_').lower() in outDict:
            outDict[key.replace(':','_').replace(' ','_').lower()][str(type(flatWxDict[key]))]=(flatWxDict[key])
        else:
            outDict[key.replace(':','_').replace(' ','_').lower()] = {str(type(flatWxDict[key])):(flatWxDict[key]) }
    filecount += 1

            
    print str(count) + " total tweets " + str(filecount) + " file count. File name = " + file
    
helper.dumpJSONtoFile("all_climate_keys_and_valtypes.json",outDict)
