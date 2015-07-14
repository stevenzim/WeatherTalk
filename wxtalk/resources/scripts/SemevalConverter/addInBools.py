from wxtalk import helper

#script to add in pos/neg/neutral boolean values.  e.g. 1 if positive 0 if anything else

#json files
files = helper.getListOfFiles(helper.getProjectPath()+'/wxtalk/resources/data/SemEval/')

def convertSentToBool(sentimentString,boolString):
    '''
    Converts sentiment string to a numeric boolean value i.e. positive = 1 everything else = 0
    Good for building boolean model
    '''
    if sentimentString == boolString:
        return 1
    return 0

for file in files:
    print file
    data = helper.loadJSONfromFile(file)
    dataToDump = []
    for dict in data:
        dict['pos_bool'] = convertSentToBool(dict['sentiment_orig'],'positive')
        dict['neg_bool'] = convertSentToBool(dict['sentiment_orig'],'negative')
        dict['neut_bool'] = convertSentToBool(dict['sentiment_orig'],'neutral')
        dataToDump.append(dict)
    helper.dumpJSONtoFile(file,dataToDump)
