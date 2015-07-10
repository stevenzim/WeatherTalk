from wxtalk import helper
import os

pathToWxDict = os.path.join(helper.getProjectPath(),'wxtalk/resources/lexicons/wx/wxWordList.txt')

wxWordList = []
iFile = open(pathToWxDict,'r')
for word in iFile:
    word = word.strip('\r\n')
    word = unicode(word,'utf8')
    wxWordList.append(word)
    
    
tweets = helper.loadJSONfromFile('tweet1.json')

tweetsToDump = []
for tweet in tweets:
    wxWordExists = False
    text = tweet['text']
    for wxWord in wxWordList:
        if wxWord in text:
            #tweetsToDump.append({'text':text,'weather':True,'word':wxWord})
            wxWordExists = True
            print wxWord
            break
    if wxWordExists == False:
        tweetsToDump.append({'text':text,'weather':False,"s1_conf": 0.0,"s5_conf": 1.0,"topic_wx_00": False})
        

helper.dumpJSONtoFile('tweetsWxWords.json',tweetsToDump)
        
