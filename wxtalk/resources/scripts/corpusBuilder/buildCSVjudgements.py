from wxtalk import helper
from random import shuffle
import csv
import os


def importCSVjudgments(csvFileName,judger,classType,apiFiles):
    '''
    Given a folder containing csv file judged by human as well as required parameters, will update original validation json files with judgements
    csvFileName = name of csv file passed back from judger
    judge = 'wx_judge_1' OR 'wx_judge_2' OR 'senti_judge_1' OR 'senti_judge_2'
    classType = 'sentiment' or 'weather'
    apiFiles = ('before' or 'after') as in before or after tweet change
    1 - creates a dictionary of all tweet ids and judgements for csv file key = id value = judgement
    2 - iterates over all json judgement files
    3 - for each tweet in current json file
        a - if id of current tweet in judgement dictionary, then update current tweet with tweet[judger] equal to judgement in dictionary
        b - else continue
    4 - write updated judgement dictionary to original file name
    usage addJudgements('test.csv','senti_judge_1','sentiment','before')
    '''
    #create judgement dictionary from csv
    csvDictList = helper.csvToDicts(csvFileName)
    judgementDictionary = {}
    for judgement in csvDictList:
        judgementDictionary[int(judgement['TweetID'])] = judgement['JUDGEMENT']
    
    tweetIDjudgementSet = set(judgementDictionary.keys())
    
    #get all json file names to update
    filePath = ''
    if classType == 'sentiment':
        filePath = helper.getProjectPath() + '/wxtalk/resources/data/LiveTweets/sentiCorpus/'
    if classType == 'weather':
        filePath = helper.getProjectPath() + '/wxtalk/resources/data/LiveTweets/wxCorpus/'
    if apiFiles == 'before':
        filePath = filePath + 'before/'
    if apiFiles == 'after':
        filePath = filePath + 'after/'
    files = helper.getListOfFiles(filePath)

    #iterate over each file and update judgement for value in judgement dictionary
    for file in files:
        fileExt = file.split('.')
        fileExt = fileExt[1]
        if fileExt =='json':
            data = helper.loadJSONfromFile(filePath + file)
            for tweet in data:
                tweetID = tweet['id']
                if tweetID in tweetIDjudgementSet:
                    tweet[judger] = judgementDictionary[tweetID]
            helper.dumpJSONtoFile(filePath + file, data)
                    

def createCSV(classType,apiFiles):
    '''
    Given a folder containing json files for particular validation corpus (e.g. sentiment before API change)
    builds a CSV file to pass onto independent reviewers
    also provide classType = ( sentiment or weather) and apiFiles = ('before' or 'after') as in before or after tweet change
    1 - Opens each json file found in path where script is run
    2 - For each json file, takes the first 300 tweets (could be changed to user specified at later date)
    3 - Tweets are grouped together (e.g. 300 of each senti class will output 900 total) and then shuffled so reviewer sees them randomly.
    The randomly shuffled data is then output to CSV and passed onto reviewers
    '''
    #set file path to random json files
    filePath = ''
    if classType == 'sentiment':
        filePath = helper.getProjectPath() + '/wxtalk/resources/data/LiveTweets/sentiCorpus/'
    if classType == 'weather':
        filePath = helper.getProjectPath() + '/wxtalk/resources/data/LiveTweets/wxCorpus/'
    if apiFiles == 'before':
        filePath = filePath + 'before/'
    if apiFiles == 'after':
        filePath = filePath + 'after/'
    files = helper.getListOfFiles(filePath)
    combinedTweets = []
    tweetsForCSV = []

    #get first 300 tweets from each file (tweets are already random in each file)
    for file in files:
        fileExt = file.split('.')
        fileExt = fileExt[1]
        if fileExt =='json':
            data = helper.loadJSONfromFile(filePath + file)
            first300 = data[:300]
            combinedTweets.extend(first300)

    #randomly mix class of each tweet together
    shuffle(tweetsForCSV)

    #write out tweets to csv file
    writer = csv.writer(open(filePath + 'tweets.csv', 'wb'))
    writer.writerow(['TweetID','JUDGEMENT','TWEET TEXT']) #header info
    for tweet in combinedTweets:
        twId = tweet['id']
        twText = tweet['text']
        writer.writerow([twId,None,unicode(twText).encode("utf-8") ])
    


