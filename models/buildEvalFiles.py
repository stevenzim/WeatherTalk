'''Creates files to be passed into SemEval grader'''

from wxtalk import helper

def buildWeatherFiles(judgementsFile):
    data = helper.loadJSONfromFile(judgementsFile)
    goldFile = open('wx-judged.tsv','w')
    predFile = open('wx-model.tsv','w')
    
    strScore = lambda score: "negative" if (score == False) else ("positive" if (score == True) else "neutral")
    for dict in data:
        goldFile.write(dict["tweet_id"] + '\t' + dict["tweet_id"] + '\t' + strScore(dict["wx_judge_1"]) + '\t' + dict["text"] + '\n')
        predFile.write(dict["tweet_id"] + '\t' + dict["tweet_id"] + '\t' + strScore(dict["wx_model"]) + '\t' + dict["text"] + '\n')
    
    goldFile.close()
    predFile.close()
