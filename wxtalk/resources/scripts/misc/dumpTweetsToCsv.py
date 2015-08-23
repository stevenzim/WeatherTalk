from wxtalk import helper
import csv

'''Given file path with json file containing tweets, dumps the id and text to tweets.csv file in folder where script is run'''


def dumpTweetsToCSV(jsonFileName):
    data = helper.loadJSONfromFile(jsonFileName)

    dataToDump = []

    for tweet in data:
        twId = tweet['id']
        twText = tweet['text']
        dataToDump.append({'id':twId,'text':twText})
        

    d = dataToDump[-200:]
    writer = csv.writer(open('tweets.csv', 'wb'))
    #oFile = open('tweets.csv', 'w')
    for tweet in d:
        twId = tweet['id']
        twText = tweet['text']
        #oFile.write( + '\n')
        writer.writerow([twId,'',unicode(twText).encode("utf-8") ])

