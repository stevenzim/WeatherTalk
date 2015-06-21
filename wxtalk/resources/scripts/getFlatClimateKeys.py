import flatdict
from wxtalk import helper
import os
import os.path

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
        #outDict[key] = flatWxDict[key]
#        if key in outDict:
#            outDict[key].append(str(type(flatWxDict[key])))
#        else:
#            outDict[key] = [str(type(flatWxDict[key]))]
        if key in outDict:
            outDict[key][str(type(flatWxDict[key]))]=(flatWxDict[key])
        else:
            outDict[key] = {str(type(flatWxDict[key])):(flatWxDict[key]) }
    filecount += 1
        #print filecount
#    except:
#        iFile = open(file)
#        oFile = open("possible errors/" + file,'w')
#        print "Error found in " + file
#        for line in iFile:
#            oFile.write(line)
#        oFile.close()
#        iFile.close()
            
    print str(count) + " total tweets " + str(filecount) + " file count. File name = " + file
    
helper.dumpJSONtoFile("all_climate_keys_and_valtypes.json",outDict)
