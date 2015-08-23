
'''Passes over directory containing json files with tweets to get total counts'''
from wxtalk import helper
files = helper.getListOfFiles(".")
count = 0
filecount = 0
for file in files:
    try:
        list = helper.loadJSONfromFile(file)
        count += len(list)
        filecount += 1
    except:
        iFile = open(file)
        oFile = open("possible errors/" + file,'w')
        print "Error found in " + file
        for line in iFile:
            oFile.write(line)
        oFile.close()
        iFile.close()
            
    print str(count) + " total tweets " + str(filecount) + " file count. File name = " + file





