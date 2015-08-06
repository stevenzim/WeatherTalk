from wxtalk import helper
from random import shuffle
import os

def createValidationFiles(apiFileName):
    '''
    builds a validation corpus from collection of all live tweets
    apiFileName = 'before/' or 'after/' as in before or after api change
    1 -passes through all classified tweet files
    2 - randomly sorts all tweets in each file
    3 - Takes maximum 2 tweets for each class in current file (i.e. 2 positive, 2 neg, 2 neutral,
            2 about weather, 2 not about weather) Adds them to appropriate list
    4 - Outputs to 5 seperate files, one for each class
    With the output files, they can then be manually split on date and then randomly sorted and output to CSV
    usage (run in directory with desried files):
    from wxtalk.resources.scripts.corpusBuilder import buildLiveTweetCorpus as tc
    tc.createValidationFiles(apiFileName)
    '''
    #api file name 
    #NOTE: You must manually load files into subfolders that are before Twitter api change and after twitter api change 
    #    and then change this line in script appropriately
    #sentiment classifier lists
    posTweets = []
    negTweets = []
    neutTweets = []

    #weather classifier lists
    weatherFalseTweets = []
    weatherTrueTweets = []


    #get all file names of classified tweets
    files = []
    for dirpath, dirnames, filenames in os.walk("."):
        for filename in [f for f in filenames if f.endswith(".json")]:
            files.append( os.path.join(dirpath, filename))

    #Main
    totalTweets = 0  
    filecount = 0
    for file in files:
        #temp lists for current file
        posCur = []
        negCur = []
        neutCur = []
        wxTrueCur = []
        wxFalseCur = []
        
        
        #load data for current file, shuffle data  and update counters
        data = helper.loadJSONfromFile(file)
        shuffle(data)
        print len(data)
        totalTweets += len(data)
        filecount += 1
        print filecount
        print len(files)
        print file
        
        #get 2 of each class from file, add desired tweet fields (e.g. text, id, creation time) and appropriate judgement field
        for tweet in data:
            # pos test
            if (tweet["ens_s1_discrete"] == 1) and (len(posCur) < 2):
                posCur.append({"text":tweet["text"],
                                "created_at":tweet["created_at"],
                                "id":tweet["id"],
                                "senti_ens":tweet["ens_s1_discrete"],
                                "senti_judge_1":None,
                                "senti_judge_2":None,
                                "senti_judge_3":None})
            #neg test
            if (tweet["ens_s1_discrete"] == -1) and (len(negCur) < 2):
                negCur.append({"text":tweet["text"],
                                "created_at":tweet["created_at"],
                                "id":tweet["id"],
                                "senti_ens":tweet["ens_s1_discrete"],
                                "senti_judge_1":None,
                                "senti_judge_2":None,
                                "senti_judge_3":None})
            #neutral test
            if (tweet["ens_s1_discrete"] == 0) and (len(neutCur) < 2):
                neutCur.append({"text":tweet["text"],
                                "created_at":tweet["created_at"],
                                "id":tweet["id"],
                                "senti_ens":tweet["ens_s1_discrete"],
                                "senti_judge_1":None,
                                "senti_judge_2":None,
                                "senti_judge_3":None})
                                
            #weather test = True
            if (tweet["w1_discrete"] == True) and (len(wxTrueCur) < 2):
                wxTrueCur.append({"text":tweet["text"],
                                "created_at":tweet["created_at"],
                                "id":tweet["id"],
                                "wx_model":tweet["w1_discrete"],
                                "wx_judge_1":None,
                                "wx_judge_2":None,
                                "wx_judge_3":None})
            #weather test = False
            if (tweet["w1_discrete"] == False) and (len(wxFalseCur) < 2):
                wxFalseCur.append({"text":tweet["text"],
                                "created_at":tweet["created_at"],
                                "id":tweet["id"],
                                "wx_model":tweet["w1_discrete"],
                                "wx_judge_1":None,
                                "wx_judge_2":None,
                                "wx_judge_3":None})
        
        #now update global sample list
        posTweets.extend(posCur)
        negTweets.extend(negCur)
        neutTweets.extend(neutCur)
        weatherTrueTweets.extend(wxTrueCur)
        weatherFalseTweets.extend(wxFalseCur)


    print str(totalTweets) + " Total tweets!"

    #randomly shuffle collected tweets
    shuffle(posTweets)
    shuffle(negTweets)
    shuffle(neutTweets)
    shuffle(weatherFalseTweets)
    shuffle(weatherTrueTweets)

    #dump lists to files
    helper.dumpJSONtoFile(helper.getProjectPath() + "/wxtalk/resources/data/LiveTweets/sentiCorpus/" + apiFileName + "PosCorpus.json",posTweets)
    helper.dumpJSONtoFile(helper.getProjectPath() + "/wxtalk/resources/data/LiveTweets/sentiCorpus/" + apiFileName + "NegCorpus.json",negTweets)
    helper.dumpJSONtoFile(helper.getProjectPath() + "/wxtalk/resources/data/LiveTweets/sentiCorpus/" + apiFileName + "NeutCorpus.json",neutTweets)
    helper.dumpJSONtoFile(helper.getProjectPath() + "/wxtalk/resources/data/LiveTweets/wxCorpus/" + apiFileName + "WxTrueCorpus.json",weatherTrueTweets)
    helper.dumpJSONtoFile(helper.getProjectPath() + "/wxtalk/resources/data/LiveTweets/wxCorpus/" + apiFileName + "WxFalseCorpus.json",weatherFalseTweets)
