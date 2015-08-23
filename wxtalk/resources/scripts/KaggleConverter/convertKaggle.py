#Steven Zimmerman
#First draft: 20-MAY-2015

#converts kaggle csv file to desired json format that will be used for building classification models
#also removes questionable data e.g. when "I don't know" score is above threshold see TODO below
#assigns a topic based on scored inputs
#assigns sentiment score based on scored inputs
#assigns temporal note based on scored inputs
#REF: https://docs.python.org/2/library/csv.html
#REF: http://stackoverflow.com/questions/19697846/python-csv-to-json

#TODO:  Confirm that it is okay to say that all S5's == 1 should be denoted as neutral sentiment...
#       Alternatively, you could do analysis of dataset to demonstrate that this is okay
#NOTE:  Currently not doing anything with fields k1-k15 --> which is used to predict the type of weather tweet is about
#       In other words, this data is currently being dumped from the file and excluded from output JSON

import csv
import json
from random import shuffle

def links_convert(text):
    '''
    Kaggle has converted each html link to "{link}" for each tweet
    This is inconsistent with Semeval dataset as well as live Twitter data.
    Therefore, "{link}" is converted to "http://somelink.com" for consistency of training classifiers
    '''
    return text.replace("{link}","http://somelink.com")

def sentiment_convert(s2TOs4score):
    '''
    Takes in fields s2-s4 scores
    Finds the max index   0 = Negative 1 = Neutral 2 = Positive
    '''
    #TODO: Consider if it is better to use -1, 0 and 1 as sentiment scores instead of neg, neutral and pos
    indexOfMax = s2TOs4score.index(max(s2TOs4score))
    if indexOfMax == 0: 
        return "negative"
    if indexOfMax == 1: 
        return "neutral"        
    if indexOfMax == 2: 
        return "positive"

def topic_convert(s5score,threshold):
    '''
    Takes in s5 field score defined as "Tweet not related to weather condition" 
    If this score is greater than 0.5, then return False, else True
    '''
    #TODO: Confirm this is the best threshold to use, research may indicate a better way to do this
    #      Need to research better way to do this, initially will be True if topic wx original > 0.5
    if float(s5score) < threshold: 
        return True
    else:
        return False
        
def temporal_convert(temporalList):
    '''
    Takes in fields w1-w4 scores
    Finds the max index   0 = present 1 = future 2 = unknown 3 = past
    '''
    #NOTE: This information is not currently used in project, as it is not necessary for primary objectives
    indexOfMax = temporalList.index(max(temporalList))
    if indexOfMax == 0: 
        return "present"
    if indexOfMax == 1: 
        return "future"        
    if indexOfMax == 2: 
        return "unknown"    
    if indexOfMax == 3: 
        return "past"            


def buildOutputDict(csvRow,sentiList,temporalList):
    '''
    Given csv row, list of sentiment scores and temporal scores, 
    converts to desired dictionary format for eventual output to JSON
    '''
    outputDict = {'id' : csvRow['id'],
                'text_orig' : csvRow['tweet'],  
                'text' : links_convert(csvRow['tweet']),  
                's1_conf' : float(sentiList[0]),
                's2_conf' : float(sentiList[1]),  
                's3_conf' : float(sentiList[2]), 
                's4_conf' : float(sentiList[3]),  
                's5_conf' : float(sentiList[4]),
                'topic_wx_00' : topic_convert(sentiList[4],0.000000001),
                'topic_wx_10' : topic_convert(sentiList[4],0.1),
                'topic_wx_20' : topic_convert(sentiList[4],0.2),
                'topic_wx_30' : topic_convert(sentiList[4],0.3),
                'topic_wx_40' : topic_convert(sentiList[4],0.4), 
                'topic_wx_50' : topic_convert(sentiList[4],0.5),
                'topic_wx_60' : topic_convert(sentiList[4],0.6),
                'topic_wx_70' : topic_convert(sentiList[4],0.7),
                'topic_wx_80' : topic_convert(sentiList[4],0.8),
                'topic_wx_90' : topic_convert(sentiList[4],0.9), 
                'topic_wx_100' : topic_convert(sentiList[4],1.0),                 
                'source' : 'Kaggle'}
    return outputDict

    
#MAIN PART OF PROGRAM. 
#Takes in Kaggle csv file and converts one row at a time to desired dictionary format.
#TODO: Could change the code from here below to be a function that takes in csv and json filenames
myList = []
currentRow = 1
with open('train.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        print currentRow
        currentRow += 1
        sentiList = [row['s1'],row['s2'],row['s3'],row['s4'],row['s5']]
        temporalList = [row['w1'],row['w2'],row['w3'],row['w4']]
        
        # Here I only save where the "I don't know" field is not the maximum
        # If "I don't know" scores highest, I have deemed it to uncertain to include
        # Based on this criteria, nearly 4000 tweets are removed!!!!
        # TODO: Research a better way to address this.  Per Udo, he recommends keeping all data
        #       Consider different removal criteria, quick glance shows that many times fields s2-s4 = 0 and s1 is > 0 and s5 < or > s1
        # NOTE: After further review of Kaggle forum and data, it seems best to not remove these at all, perhaps consider taking into account the uncertainty label
        #       see https://www.kaggle.com/c/crowdflower-weather-twitter/forums/t/6267/s1-is-i-don-t-know-if-it-is-weather-related-or-i-don-t-know-if-it-is-positive
        
        myList.append(buildOutputDict(row,sentiList,temporalList))
        # if sentiList.index(max(sentiList[:4])) != 0:
            # myList.append(buildOutputDict(row,sentiList,temporalList))
        # else:
            # print row['id']
            # totalRemoved += 1

#SHUFFLE THE LIST FOR PREP OF TRAINING/TEST SETS
shuffle(myList)
sampleSize = len(myList)
trainSize = int(.8*sampleSize)
trainSet = myList[:trainSize]
testSet = myList[trainSize:]

#Pretty print to JSON
#output train set
with open('train.json', 'w') as outfile:
    json.dump(trainSet, outfile ,sort_keys=True, indent=4, separators=(',', ': '))
    
    
#output test set
with open('test.json', 'w') as outfile:
    json.dump(testSet, outfile ,sort_keys=True, indent=4, separators=(',', ': '))
