#Steven Zimmerman
#First draft: 21-MAY-2015

#converts semeval tsv file to desired json format that will be used for building sentiment classification models
#removes missing tweets from file denoted by 'Not Available'
#REF: http://alt.qcri.org/semeval2015/task10/
#REF: http://stackoverflow.com/questions/19697846/python-csv-to-json

#TODO:  Consider feature reduction.  e.g. change @username to user and all http links --> URL
#TODO:	Consider is it better to leave classes as neg,neut,pos or convert to -1,0,1

# usage 'python .\convertSemeval.py TestFile.csv semeval-train.json'

import csv
import json
import sys

args = sys.argv
inputCSV = args[1]
outputJSON = args[2]


def convertSentToNum(sentimentString):
    '''
    Converts sentiment string to a numeric value i.e. positive = 1
    '''
    if sentimentString == 'positive':
        return 1
    if sentimentString == 'neutral':
        return 0
    if sentimentString == 'negative':
        return -1

def buildOutputDict(csvRow):
    '''
    Given csv row
    converts to desired dictionary format for eventual output to JSON
    '''
    outputDict = {'tweet_id' : csvRow['tweet_id'],
                'semeval_id' : csvRow['semeval_id'],
                'text' : csvRow['tweet'],  
                #'text_converted' : links_convert(csvRow['tweet']),  
                #'loc_state' : csvRow['state'],
                #'loc_city' : csvRow['location'],
                'sentiment_orig' : csvRow['sentiment'],
                'sentiment_num' : convertSentToNum(csvRow['sentiment']),
                #'sentiment_converted' : sentiment_convert(sentiList[1:4]), 
                #'topic_wx_orig' : sentiList[-1],
                #'topic_wx_converted' : topic_convert(sentiList[-1]),  
                #'uncertainty_score' : sentiList[0],
                'source' : 'Semeval-train'}
    return outputDict

    
#MAIN PART OF PROGRAM. 
#Takes in semeval csv file and converts one row at a time to desired dictionary format.  
#NOTE: You must convert semeval file from tab delimited to comma delimited and add correct headers

myList = []
currentRow = 1
with open(inputCSV) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        print currentRow
        currentRow += 1
        if row['tweet'] == 'Not Available':
            continue
        else:
            myList.append(buildOutputDict(row))



#Pretty print to JSON
#TODO: Reorganize code, so that I can import the helper function
#with open('semeval-train.json', 'w') as outfile:
#with open('Test.json', 'w') as outfile:
with open(outputJSON, 'w') as outfile:
    json.dump(myList, outfile ,sort_keys=True, indent=4, separators=(',', ': '))
