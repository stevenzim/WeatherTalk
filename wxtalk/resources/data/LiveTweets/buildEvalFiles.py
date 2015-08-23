'''Creates files to be passed into SemEval grader'''

from wxtalk import helper

def buildWeather(judgementsFile):
    data = helper.loadJSONfromFile(judgementsFile)
    goldFile = open('wx-judged.tsv','w')
    predFile = open('wx-model.tsv','w')
    strScore = lambda score: "negative" if (score == False) else ("positive" if (score == True) else "neutral")
    for dict in data:
        goldFile.write(str(dict["id"]) + '\t' + str(dict["id"]) + '\t' + strScore(dict["wx_judge_1"]) + '\t' + "DUMMY TEXT" + '\n')
        predFile.write(str(dict["id"]) + '\t' + str(dict["id"]) + '\t' + strScore(dict["wx_model"]) + '\t' + "DUMMY TEXT" + '\n')
    goldFile.close()
    predFile.close()

def buildSenti(judgementsFile):
    data = helper.loadJSONfromFile(judgementsFile)
    goldFile = open('senti-judged.tsv','w')
    predFile = open('senti-model.tsv','w')
    
    strScore = lambda score: "negative" if (score == -1) else ("positive" if (score == 1) else "neutral")
    for dict in data:
        goldFile.write(str(dict["id"]) + '\t' + str(dict["id"]) + '\t' + strScore(dict["senti_judge_1"]) + '\t' + "DUMMY TEXT" + '\n')
        predFile.write(str(dict["id"]) + '\t' + str(dict["id"]) + '\t' + strScore(dict["senti_ens"]) + '\t' + "DUMMY TEXT" + '\n')
    goldFile.close()
    predFile.close()


    
