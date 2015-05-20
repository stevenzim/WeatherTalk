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

def topic_convert(s5score):
    '''
    Takes in s5 field score defined as "Tweet not related to weather condition" 
    If this score is greater than 0.5, then return False, else True
    '''
    #TODO: Confirm this is the best threshold to use, research may indicate a better way to do this
    #      Need to research better way to do this, initially will be True if topic wx original > 0.5
    if sentiList[-1] > 0.5: 
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
                'text_converted' : links_convert(csvRow['tweet']),  
                'loc_state' : csvRow['state'],
                'loc_city' : csvRow['location'],
                'sentiment_orig' : sentiList,
                'sentiment_converted' : sentiment_convert(sentiList[1:4]), 
                'temporal_orig' : temporalList,
                'temporal_converted' : temporal_convert(temporalList), 
                'topic_wx_orig' : sentiList[-1],
                'topic_wx_converted' : topic_convert(sentiList[-1]),  
                'source' : 'Kaggle'}
    return outputDict

    
#MAIN PART OF PROGRAM. 
#Takes in Kaggle csv file and converts one row at a time to desired dictionary format.
#TODO: Could change the code from here below to be a function that takes in csv and json filenames
myList = []
currentRow = 1
totalRemoved = 0    
with open('train-edited-test.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        #print currentRow
        currentRow += 1
        sentiList = [row['s1'],row['s2'],row['s3'],row['s4'],row['s5']]
        temporalList = [row['w1'],row['w2'],row['w3'],row['w4']]
        
        # Here I only save where the "I don't know" field is not the maximum
        # If "I don't know" scores highest, I have deemed it to uncertain to include
        # Based on this criteria, nearly 4000 tweets are removed!!!!
        # TODO: Research a better way to address this.  Per Udo, he recommends keeping all data
        #       Consider different removal criteria, quick glance shows that many times fields s2-s4 = 0 and s1 is > 0 and s5 < or > s1
        if sentiList.index(max(sentiList[:4])) != 0:
            myList.append(buildOutputDict(row,sentiList,temporalList))
        else:
            print row['id']
            totalRemoved += 1

    print totalRemoved   


#Pretty print to JSON
#TODO: Reorganize code, so that I can import the helper function
with open('test.json', 'w') as outfile:
    json.dump(myList, outfile ,sort_keys=True, indent=4, separators=(',', ': '))