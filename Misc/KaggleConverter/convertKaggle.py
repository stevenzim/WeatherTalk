#converts kaggle csv file to desired json format
#also removes questionable data
#assigns a topic based on scored inputs
#assigns sentiment score based on scored inputs
#assigns temporal note based on scored inputs
#REF: https://docs.python.org/2/library/csv.html
#REF: http://stackoverflow.com/questions/19697846/python-csv-to-json

import csv
import json


def buildOutputDict(csvRow):
    outputDict = {'id':csvRow['id'],
                'loc_state':csvRow['state']}
    return outputDict

myList = []    
with open('train-edited-test.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        sentiList = [row['s1'],row['s2'],row['s3'],row['s4'],row['s5']]
        temporalList = [row['w1'],row['w2'],row['w3'],row['w4']]
        #if list.index(max(list))
        myList.append(buildOutputDict(row))
        print sentiList


with open('test.json', 'w') as outfile:
    json.dump(myList, outfile ,sort_keys=True, indent=4, separators=(',', ': '))