from wxtalk import helper

filepath = "../../Tweets"
files = helper.getListOfFiles(filepath)

print "Total Files to process = " + str(len(files))
filesComplete = 0
obamaCount = 0
totalCount = 0

outputList = []

for file in files:
    print "Files completed = " + str(filesComplete)
    filesComplete += 1
    updateList = []
    listOfDicts = helper.loadJSONfromFile(filepath + "/" + file)
    totalCount += len(listOfDicts)
    for dict in listOfDicts:
        dict = helper.addStringTestTopic(dict,'text',"obama","topic_obama")
        if dict["topic_obama"]:
            obamaCount += 1
            outputList.append({"text":dict['text']})
        updateList.append(dict)
        
    print "Total obama count = " + str(obamaCount)
    print "Total tweet count = " + str(totalCount)
    print "\n"


helper.dumpJSONtoFile("ObamaText.txt",outputList)
