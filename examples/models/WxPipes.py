'''Weather classification model building pipeline and functions'''
from wxtalk.model import transformers as tran
from wxtalk import helper

import string


from sklearn.pipeline import (Pipeline,FeatureUnion)
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import (CountVectorizer, TfidfTransformer, TfidfVectorizer)

from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier

import sklearn.externals.joblib as joblib

#for GridSearchCV examples
from sklearn.grid_search import GridSearchCV
#from __future__ import print_function
from pprint import pprint
from time import time
import logging



#########################################
#####all features pipeline###############
#########################################


####---------------n-grams------------------####

#word grams
unigrams = Pipeline([\
            ('docs',tran.DocsExtractor('normalised_string')),\
            ('count',tran.CountVectorizer(tokenizer=string.split,ngram_range=(1, 1) ,binary=True,min_df=1))])                 
bigrams = Pipeline([\
            ('docs',tran.DocsExtractor('normalised_string')),\
            ('count',tran.CountVectorizer(tokenizer=string.split,ngram_range=(1, 2) ,binary=True,min_df=1))])   

#stem-grams
unistems = Pipeline([\
            ('docs',tran.DocsExtractor('stem_string')),\
            ('count',tran.CountVectorizer(tokenizer=string.split,ngram_range=(1, 1) ,binary=True,min_df=1))])                 
bistems = Pipeline([\
            ('docs',tran.DocsExtractor('stem_string')),\
            ('count',tran.CountVectorizer(tokenizer=string.split,ngram_range=(1, 2) ,binary=True,min_df=1))])  

#char-grams
charGrams = Pipeline([\
            ('docs',tran.DocsExtractor('normalised_string')),\
            ('count',tran.CountVectorizer(analyzer='char',ngram_range=(3, 5) ,binary=True,min_df=1))])

            
###--------------POS -------------------###
posCounts = Pipeline([\
            ('pos-counts-dict',tran.POScountExtractor()),\
            ('pos-vec',tran.DictVectorizer())])
            
###---------------clusters--------------###
#CMU 1000
cmuClusterFeatures = Pipeline([\
            ('clusters',tran.ClusterExtractor(['normalised_token_list'])),\
            ('count',tran.CountVectorizer(tokenizer=string.split,ngram_range=(1, 1) ,binary=False,\
                     vocabulary = helper.loadJSONfromFile(helper.getProjectPath() + '/wxtalk/resources/lexicons/CMU/CMU-cluster-vocab.json')))])    

 
#WXclf features
features = FeatureUnion([
            #('unigram-count',unigrams),
            ('bigram-count',bigrams),
            #('unistems-count',unistems),
            #('bistems-count',bistems),
            ('charGrams-count',charGrams),
            #('pos-count',posCounts),
            ('cmu-cluster',cmuClusterFeatures)
            ]) 
clf = Pipeline([\
            ('features',features),
            ('clf',LogisticRegression(penalty = 'l1',C = 0.1))])

#^^^^^^^^^^^^^^^^^BASELINE^^^^^^^^^^^^^^^^^^^^^^^#
#clf =Pipeline([\
#            ('features',features),
#            ('clf',LogisticRegression(penalty = 'l1',C = 1.0))])

(clf,modelName,'FINAL MODEL-unigrams-50-l1-c.3',ysKeyName='topic_wx_50')
(clf,modelName,'ABLATION-MODEL-w/out BISTEMS/POSCOUNTS-50-l1-c.1',ysKeyName='topic_wx_50')
modelName = 'all-features'
def finalTest(clf,modelName,descript,ysKeyName='topic_wx_50',userNorm = None,urlNorm = None,hashNormalise=False,digitNormalise=False):
    projPath = helper.getProjectPath()
    
    print "Building Model"
    #TRAIN 2015
    inFile = projPath + '/wxtalk/resources/data/KagSem/TrainWeatherTriples.json'
    data = helper.loadJSONfromFile(inFile)           
    ed = tran.TweetTransformer(userNorm = userNorm,urlNorm = urlNorm,hashNormalise=hashNormalise,digitNormalise=digitNormalise)
    tweetsList, ysList = ed.transform(data,ysKeyName = ysKeyName)
    ### DEV 2015
    inFile = projPath + '/wxtalk/resources/data/KagSem/DevWeatherTriples.json'
    data = helper.loadJSONfromFile(inFile)           
    ed = tran.TweetTransformer(userNorm = userNorm,urlNorm = urlNorm,hashNormalise=hashNormalise,digitNormalise=digitNormalise)
    tweetsListDev, expected_ysDev = ed.transform(data,ysKeyName = ysKeyName)
    
    #Combine into one train set and build model
    tweetsList.extend(tweetsListDev), ysList.extend(expected_ysDev)
    clf.fit(tweetsList,ysList)
    joblib.dump(clf, projPath + '/wxtalk/resources/data/KagSem/pickles/model.pkl') 
    loadedpipe = joblib.load(projPath + '/wxtalk/resources/data/KagSem/pickles/model.pkl')
    
    print "Model built, predicting results"
    print "Predicting on Test Data"
    loadedpipe = joblib.load(projPath + '/wxtalk/resources/data/KagSem/pickles/model.pkl')
    #test
    inFile = projPath + '/wxtalk/resources/data/KagSem/TestWeatherTriples.json'
    data = helper.loadJSONfromFile(inFile)  
    ed = tran.TweetTransformer(userNorm = userNorm,urlNorm = urlNorm,hashNormalise=hashNormalise,digitNormalise=digitNormalise)
    transformedTweets, expected_ys = ed.transform(data,ysKeyName = ysKeyName)
    predicted_ys = loadedpipe.predict(transformedTweets)
    evalMetrics =  helper.evaluateResults(expected_ys,predicted_ys)
    oFile = open('WXmetrics-'+modelName+'.txt','a')
    oFile.write('***********' + ysKeyName + ' desc: ' +descript+'***********\n')
    oFile.write(evalMetrics)
    oFile.close()
    
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

def testingPipeline(clf,modelName,descript,ysKeyName='topic_wx_50',userNorm = None,urlNorm = None,hashNormalise=False,digitNormalise=False):
    projPath = helper.getProjectPath()
    print "Building Model"
    inFile = projPath + '/wxtalk/resources/data/KagSem/TrainWeatherTriples.json'
    data = helper.loadJSONfromFile(inFile)        
    ed = tran.TweetTransformer(userNorm = userNorm,urlNorm = urlNorm,hashNormalise=hashNormalise,digitNormalise=digitNormalise)
    transformedTweets, ysList = ed.transform(data,ysKeyName = ysKeyName)
    clf.fit(transformedTweets,ysList)
    joblib.dump(clf, projPath + '/wxtalk/resources/data/KagSem/pickles/kaggle-proto.pkl') 
    loadedpipe = joblib.load(projPath + '/wxtalk/resources/data/KagSem/pickles/kaggle-proto.pkl')
    
    print "Predicting on Test Data"
    '''Must complete steps in 1d  and load clfpipeline first'''
    #TODO: Add in confusion matrix --> vvvv
    #       from sklearn.metrics import confusion_matrix
    #       self.confusionMatrix = confusion_matrix(self.Y_set,y_pred)
    loadedpipe = joblib.load(projPath + '/wxtalk/resources/data/KagSem/pickles/kaggle-proto.pkl')
    #test
    inFile = projPath + '/wxtalk/resources/data/KagSem/DevWeatherTriples.json'
    data = helper.loadJSONfromFile(inFile)  
    ed = tran.TweetTransformer(userNorm = userNorm,urlNorm = urlNorm,hashNormalise=hashNormalise,digitNormalise=digitNormalise)
    transformedTweets, expected_ys = ed.transform(data,ysKeyName = ysKeyName)
    predicted_ys = loadedpipe.predict(transformedTweets)
    evalMetrics =  helper.evaluateResults(expected_ys,predicted_ys)
    oFile = open('WXmetrics-'+modelName+'.txt','a')
    oFile.write('***********' + ysKeyName + ' desc: ' +descript+'***********\n')
    oFile.write(evalMetrics)
    oFile.close()
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
    
    


def updateJudgements(userNorm = None,urlNorm = None,hashNormalise=False,digitNormalise=False,\
                    clfKeyName = "clf_wx_score",\
                    modelBinaryPath = None,\
                    predictionFile = '../../wxtalk/resources/data/KagSem/LiveCorpusWithTriples.json',\
                    goldFile = '../../wxtalk/resources/data/KagSem/LiveCorpusScored.json'):
    print "Prediction on Validation Data"
    '''Assumes that pickle files contain the desired pipeline'''
    loadedpipe = joblib.load('../../wxtalk/resources/data/KagSem/pickles/model.pkl')
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



