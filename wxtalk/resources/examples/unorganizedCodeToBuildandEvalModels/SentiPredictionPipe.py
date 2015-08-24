#for all examples
from wxtalk.model import (predictors,ensemblers)
from wxtalk import helper

import string

import time

start_time = time.time()
print("Total elapsed time--- %s seconds ---" % (time.time() - start_time))
testDataPath = helper.getProjectPath() + "/wxtalk/resources/data/SemEval/"
test2013data = helper.loadJSONfromFile(testDataPath + 'SemTest2013.json')
test2014data = helper.loadJSONfromFile(testDataPath + 'SemTest2014.json')
test2015data = helper.loadJSONfromFile(testDataPath + 'SemTest2015.json')
outTest2013path = testDataPath + 'SemTest2013Preds.json'
outTest2014path = testDataPath + 'SemTest2014Preds.json'
outTest2015path = testDataPath + 'SemTest2015Preds.json'

modelList = [predictors.NRCmodelMetaData,\
            predictors.KLUEmodelMetaData,\
            predictors.GUMLTLTmodelMetaData]


#MODEL PREDICTIONS
#predict 2013 individual models
results = predictors.makePredictions(modelList,test2013data)
helper.dumpJSONtoFile(outTest2013path,results)
print("Total elapsed time--- %s seconds ---" % (time.time() - start_time))
#predict 2014 individual models
results = predictors.makePredictions(modelList,test2014data)
helper.dumpJSONtoFile(outTest2014path,results)
print("Total elapsed time--- %s seconds ---" % (time.time() - start_time))
#predict 2015 individual models
results = predictors.makePredictions(modelList,test2015data)
helper.dumpJSONtoFile(outTest2015path,results)
print("Total elapsed time--- %s seconds ---" % (time.time() - start_time))
#ENSEMBLE PREDICTIONS
#params
ensembleAll = {"id":'ens_s1',\
                    "model_id_list":['s1','s2','s3'],\
                    "model_classes":[-1,0,1],\
                    "description":"All"}
ensembleNoGUMLT = {"id":'ens_s2',\
                    "model_id_list":['s1','s2'],\
                    "model_classes":[-1,0,1],\
                    "description":"GUMLT-Held-Out"}
ensembleNoKLUE = {"id":'ens_s3',\
                    "model_id_list":['s1','s3'],\
                    "model_classes":[-1,0,1],\
                    "description":"KLUE-Held-Out"}
ensembleNoNRC = {"id":'ens_s4',\
                    "model_id_list":['s2','s3'],\
                    "model_classes":[-1,0,1],\
                    "description":"NRC-Held-Out"}

ensembleParamList = [ensembleAll,ensembleNoGUMLT,ensembleNoKLUE,ensembleNoNRC]
#data
test2013data = helper.loadJSONfromFile(outTest2013path)
test2014data = helper.loadJSONfromFile(outTest2014path)
test2015data = helper.loadJSONfromFile(outTest2015path)

#predict 2013 ensembles
results = ensemblers.compileEnsemble(ensembleParamList,test2013data)
helper.dumpJSONtoFile(outTest2013path,results)

#predict 2014 ensembles
results = ensemblers.compileEnsemble(ensembleParamList,test2014data)
helper.dumpJSONtoFile(outTest2014path,results)

#predict 2015 ensembles
results = ensemblers.compileEnsemble(ensembleParamList,test2015data)
helper.dumpJSONtoFile(outTest2015path,results)
print("Total elapsed time--- %s seconds ---" % (time.time() - start_time))

def outputScoreFiles(discreteEnsembleID,results):
    goldFile = open('ens-gold2013.tsv','w')
    predFile = open('ens-pred2013.tsv','w')
    
    strScore = lambda score: "negative" if (score == -1) else ("positive" if (score == 1) else "neutral")
    for dict in results:
        goldFile.write(dict["tweet_id"] + '\t' + dict["semeval_id"] + '\t' + dict["sentiment_orig"] + '\t' + dict["text"] + '\n')
        predFile.write(dict["tweet_id"] + '\t' + dict["semeval_id"] + '\t' + strScore(dict[discreteEnsembleID]) + '\t' + dict["text"] + '\n')
    
    goldFile.close()
    predFile.close()

def testingPipeline(clf,ysKeyName='topic_wx_00',userNorm = None,urlNorm = None,hashNormalise=False,digitNormalise=False):
    print "Building Model"
    inFile = '../../wxtalk/resources/data/KagSem/TrainWeatherTriples.json'
    data = helper.loadJSONfromFile(inFile)        
    ed = tran.TweetTransformer(userNorm = userNorm,urlNorm = urlNorm,hashNormalise=hashNormalise,digitNormalise=digitNormalise)
    transformedTweets, ysList = ed.transform(data,ysKeyName = ysKeyName)
    clfpipeline.fit(transformedTweets,ysList)
    joblib.dump(clfpipeline, '../../wxtalk/resources/data/KagSem/pickles/kaggle-proto.pkl') 
    loadedpipe = joblib.load('../../wxtalk/resources/data/KagSem/pickles/kaggle-proto.pkl')
    
    print "Predicting on Test Data"
    '''Must complete steps in 1d  and load clfpipeline first'''
    #TODO: Add in confusion matrix --> vvvv
    #       from sklearn.metrics import confusion_matrix
    #       self.confusionMatrix = confusion_matrix(self.Y_set,y_pred)
    loadedpipe = joblib.load('../../wxtalk/resources/data/KagSem/pickles/kaggle-proto.pkl')
    #test
    inFile = '../../wxtalk/resources/data/KagSem/TestWeatherTriples.json'
    data = helper.loadJSONfromFile(inFile)  
    ed = tran.TweetTransformer(userNorm = userNorm,urlNorm = urlNorm,hashNormalise=hashNormalise,digitNormalise=digitNormalise)
    transformedTweets, expected_ys = ed.transform(data,ysKeyName = ysKeyName)
    predicted_ys = loadedpipe.predict(transformedTweets)
    print helper.evaluateResults(expected_ys,predicted_ys)
    
    print "Writing out evaluation files for scorer"
    wxClassPreds = predicted_ys.tolist()
    count = 0 
    for dict in data:
        keydropped = dict.pop("tagged_tweet_triples",None)  #stored as variable in order to supress print to screen
        dict["clf_wx_score"] = wxClassPreds[count]
        count += 1
    
    goldFile = open('wx-gold.tsv','w')
    predFile = open('wx-pred.tsv','w')
    
    strScore = lambda score: "negative" if (score == 0) else ("positive" if (score == 1) else "neutral")
    for dict in data:
        goldFile.write(dict["tweet_id"] + '\t' + dict["tweet_id"] + '\t' + strScore(dict[ysKeyName]) + '\t' + dict["text"] + '\n')
        predFile.write(dict["tweet_id"] + '\t' + dict["tweet_id"] + '\t' + strScore(dict["clf_wx_score"]) + '\t' + dict["text"] + '\n')
    
    goldFile.close()
    predFile.close()
    #helper.dumpJSONtoFile(outFile,data) 
    
    print "Prediction on Validation Data"
    '''Assumes that pickle files contain the desired pipeline'''
    loadedpipe = joblib.load('../../wxtalk/resources/data/KagSem/pickles/kaggle-proto.pkl')
    inFile = '../../wxtalk/resources/data/KagSem/LiveCorpusWithTriples.json'
    outFile = '../../wxtalk/resources/data/KagSem/LiveCorpusScored.json'
    data = helper.loadJSONfromFile(inFile)           
    ed = tran.TweetTransformer(userNorm = userNorm,urlNorm = urlNorm,hashNormalise=hashNormalise,digitNormalise=digitNormalise)
    transformedTweets = ed.transform(data)
    predicted_ys = loadedpipe.predict(transformedTweets)
    wxPredictList = predicted_ys.tolist()
    #TODO: Create a fully working function out of this, needs to be tested
    #       Should also have error handling for when counts don't match
    #TODO: You could also add in topic classification here e.g. dict["topic_wx"] = topic_wx[count]
    count = 0 
    for dict in data:
        keydropped = dict.pop("tagged_tweet_triples",None)  #stored as variable in order to supress print to screen
        dict["clf_wx_score"] = wxPredictList[count]
        count += 1
    
    helper.dumpJSONtoFile(outFile,data)   #dump live tweets with classifer predictions added to json
    print "Done"


def updateJudgements(userNorm = None,urlNorm = None,hashNormalise=False,digitNormalise=False,\
                    clfKeyName = "clf_wx_score",\
                    modelBinaryPath = None,\
                    predictionFile = '../../wxtalk/resources/data/KagSem/LiveCorpusWithTriples.json',\
                    goldFile = '../../wxtalk/resources/data/KagSem/LiveCorpusScored.json'):
    print "Prediction on Validation Data"
    '''Assumes that pickle files contain the desired pipeline'''
    loadedpipe = joblib.load('../../wxtalk/resources/data/KagSem/pickles/kaggle-proto.pkl')
    predictionData = helper.loadJSONfromFile(predictionFile) 
    goldData = helper.loadJSONfromFile(goldFile) 
    ed = tran.TweetTransformer(userNorm = userNorm,urlNorm = urlNorm,hashNormalise=hashNormalise,digitNormalise=digitNormalise)
    transformedTweets = ed.transform(predictionData)
    predicted_ys = loadedpipe.predict(transformedTweets)
    wxPredictList = predicted_ys.tolist()
    count = 0 
    for dict in predictionData:
        predictTweetId = dict["id"]
        goldTweetId = goldData[count]["id"]
        if predictTweetId != goldTweetId:
            raise Exception ("Gold and prediciton files not the same order!!! Perhaps wrong files??")
        else:
            goldData[count][clfKeyName ] = wxPredictList[count]
            #keydropped = dict.pop("tagged_tweet_triples",None)  #stored as variable in order to supress print to screen
            dict[clfKeyName ] = wxPredictList[count]
        count += 1
    
    helper.dumpJSONtoFile(goldFile,goldData)   #dump live tweets with classifer predictions added to json
    print "Done"




