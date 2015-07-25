#for all examples
from wxtalk.modelbuilder import transformers as tran
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


#1 - Extract NLP Triples
inFile = '../../wxtalk/resources/data/KagSem/TrainWeather.json'
outFile = '../../wxtalk/resources/data/KagSem/TrainWeatherTriples.json'
helper.extractTweetNLPtriples(inFile,outFile)

inFile = '../../wxtalk/resources/data/KagSem/TestWeather.json'
outFile = '../../wxtalk/resources/data/KagSem/TestWeatherTriples.json'
helper.extractTweetNLPtriples(inFile,outFile)

#########################################
#####all features pipeline###############
#########################################


####---------------n-grams------------------####
#TODO: Investigate options, such as max_df and max_features, perhaps try it with different classifiers
## word-grams
#TODO: Investigate non-contiguous tokens (to time consuming for project, future work)

#wordGramCount = Pipeline([\
#            ('docs',tran.DocsExtractor()),\
#            ('count',tran.CountVectorizer(tokenizer=string.split,max_df= 0.75,max_features=50000,ngram_range=(1, 1) ,binary=False))])

wordGramCount = Pipeline([\
            ('docs',tran.DocsExtractor()),\
            ('count',tran.CountVectorizer(tokenizer=string.split,ngram_range=(1, 4) ,binary=True,min_df=1))])                 

NRCwordgrams = Pipeline([\
            ('docs',tran.DocsExtractor()),\
            ('count',tran.CountVectorizer(tokenizer=string.split,ngram_range=(1, 4) ,binary=True,min_df=1))])  
     
#char-grams
#TODO: Waiting to hear back from authors regarding window position, is accross entire tweet or individual words
#TODO: investigate options for ngram range (they use 3,5 in paper)
#charGramCount = Pipeline([\
#            ('docs',tran.DocsExtractor()),\
#            ('count',tran.CountVectorizer(analyzer='char',max_df= 0.75,max_features=50000,ngram_range=(3, 3) ))])
NRCchargrams = Pipeline([\
            ('docs',tran.DocsExtractor()),\
            ('count',tran.CountVectorizer(tokenizer=string.split,analyzer='char',ngram_range=(3, 5) ,binary=True,min_df=1))])
NRCchargrams = Pipeline([\
            ('docs',tran.DocsExtractor()),\
            ('count',tran.CountVectorizer(analyzer='char',ngram_range=(3, 5) ,binary=True,min_df=1))])

            
###--------------POS -------------------###
posCounts = Pipeline([\
            ('pos-counts-dict',tran.POScountExtractor()),\
            ('pos-vec',tran.DictVectorizer())])
            
###---------------clusters--------------###
#CMU 1000
cmuClusterFeatures = Pipeline([\
            ('clusters',tran.ClusterExtractor()),\
            ('count',tran.CountVectorizer(tokenizer=string.split,ngram_range=(1, 1) ,binary=False,\
                     vocabulary = helper.loadJSONfromFile(helper.getProjectPath() + '/wxtalk/resources/lexicons/CMU/CMU-cluster-vocab.json')))])    


#EMOTICON
#TODO: Use wikipedia per 2013 paper

###---------------encodings-------------###
#ALL CAPS
allCapsCount = Pipeline([\
            ('caps-counts-dict',tran.CapsCountExtractor()),\
            ('caps-vec',tran.DictVectorizer())])

#HASH TAGS
hashTagCount = Pipeline([\
            ('hashtag-counts-dict',tran.HashCountExtractor()),\
            ('hashtag-vec',tran.DictVectorizer())])

#elongated words
elongatedWordCount = Pipeline([\
            ('elong-counts-dict',tran.ElongWordCountExtractor()),\
            ('elong-vec',tran.DictVectorizer())])
#punctuations
puncFeatures = Pipeline([\
            ('punct-features-dict',tran.PunctuationFeatureExtractor()),\
            ('punct-vec',tran.DictVectorizer())])

#emoticons
emotiFeatures = Pipeline([\
            ('emoti-features-dict',tran.EmoticonExtractor('emoticon')),\
            ('emoti-vec',tran.DictVectorizer())])

###-------------Negation----------------###
negateCounts = Pipeline([\
            ('negate-counts-dict',tran.NegationCountExtractor()),\
            ('negate-vec',tran.DictVectorizer())])
 
#NRC features
features = FeatureUnion([
            ('lex-man-feats',lexManualFeatures),
            ('lex-auto-feats',lexAutoFeatures),
            ('word-gram-count',NRCwordgrams),
            ('char-gram-count',NRCchargrams),
            ('pos-count',posCounts),
            ('cmu-cluster',cmuClusterFeatures),
            ('all-caps-count',allCapsCount),
            ('hashtags-count',hashTagCount),
            ('elong-count',elongatedWordCount),
            ('punctuation-feats',puncFeatures),
            ('emoti-feats',emotiFeatures),
            ]) 
clfpipeline = Pipeline([\
            ('features',features),
            ('clf',LogisticRegression(penalty = 'l1',C = .2))])
#**********Other papers features***
#TODO: Decide which ones, very much like the features from KLUE paper
#RTRGO/prototype
#rtrgoFeatures = Pipeline([\
#            ('text-feats-dict',tran.TextFeaturesExtractor(keysToDrop=[])),\
#            ('text-feats-vec',tran.DictVectorizer())])
#KLUE
KLUEwordgrams = Pipeline([\
            ('docs',tran.DocsExtractor()),\
            ('count',tran.CountVectorizer(tokenizer=string.split,ngram_range=(1, 2) ,binary=True,min_df=1))])

negateCounts = Pipeline([\
            ('negate-counts-dict',tran.NegationCountExtractor()),\
            ('negate-vec',tran.DictVectorizer())])
            
KLUEstems = Pipeline([\
            ('docs',tran.DocsExtractor('stem_string')),\
            ('count',tran.CountVectorizer(tokenizer=string.split,ngram_range=(1, 2) ,binary=True,min_df=1))])

KLUEtokenCount = Pipeline([\
            ('token-count-dict',tran.TokenCountExtractor()),\
            ('token-count-vec',tran.DictVectorizer())])
            
KLUEpolarity = Pipeline([\
            ('polarity-dict',tran.KLUEpolarityExtractor('klue-afinn',tokenListKeyName= 'negated_token_list')),\
            ('polarity-vec',tran.DictVectorizer())])
#KLUEpolarity = Pipeline([\
#            ('docs',tran.DocsExtractor(hashNormalise=False)),\
#            ('polarity-dict',tran.KLUEpolarityExtractor('klue-afinn')),\
#            ('polarity-vec',tran.DictVectorizer())])

KLUEemotiacro = Pipeline([\
            ('emoti-acro-dict',tran.KLUEpolarityExtractor('klue-both',tokenListKeyName= 'normalised_token_list')),\
            ('emoti-acro-vec',tran.DictVectorizer())])            
#KLUEemotiacro = Pipeline([\
#            ('docs',tran.DocsExtractor(hashNormalise=False)),\
#            ('emoti-acro-dict',tran.KLUEpolarityExtractor('klue-both')),\
#            ('emoti-acro-vec',tran.DictVectorizer())])
#KLUE features
features = FeatureUnion([
            ('word-gram-count',KLUEwordgrams),
            ('negate-feats',negateCounts),
            ('klue-token-count', KLUEtokenCount),
            ('klue-polarity', KLUEpolarity),
            ('klue-emoti-acro', KLUEemotiacro),
            ])
            
clfpipeline = Pipeline([\
            ('features',features),
            ('clf',LogisticRegression(penalty = 'l2',C = 0.25))])
            

#----------------            
#GU-MLT
GUMLTwordGrams = Pipeline([\
            ('docs',tran.DocsExtractor(transformedTweetKeyName = 'normalised_string')),\
            ('count',tran.CountVectorizer(tokenizer=string.split,ngram_range=(1, 1) ,binary=True))])
GUMLTstems = Pipeline([\
            ('docs',tran.DocsExtractor('stem_string')),\
            ('count',tran.CountVectorizer(tokenizer=string.split,ngram_range=(1, 1) ,binary=True))])
negateCounts = Pipeline([\
            ('negate-counts-dict',tran.NegationCountExtractor()),\
            ('negate-vec',tran.DictVectorizer())])
GUMLTClusterFeatures = Pipeline([\
            ('clusters',tran.ClusterExtractor(['collapsed_token_list','raw_token_list','normalised_token_list'])),\
            ('count',tran.CountVectorizer(tokenizer=string.split,ngram_range=(1, 1) ,binary=False,\
                     vocabulary = helper.loadJSONfromFile(helper.getProjectPath() + '/wxtalk/resources/lexicons/CMU/CMU-cluster-vocab.json')))])   
GUMLTpolarity = Pipeline([\
            ('polarity-dict',tran.GUMLTsentiWordNetExtractor(tokenListKeyName= 'collapsed_token_list')),\
            ('polarity-vec',tran.DictVectorizer())])
#GM-MLT features
features = FeatureUnion([
            ('word-gram-count',GUMLTwordGrams),
            ('stem-gram-count',GUMLTstems ),
            ('negate-feats',negateCounts),
            ('cmu-cluster',GUMLTClusterFeatures),
            ('gmmlt-polarity', GUMLTpolarity),
            ])

clfpipeline = Pipeline([\
             ('features',features),
             ('clf',LogisticRegression(penalty = 'l2',C = 0.4))])
#finalTest(clfpipeline,digitNormalise=True)

#***********BLENDED/TeamX features*************
#favourite features
features = FeatureUnion([
            ('lex-man-feats',lexManualFeatures),
            ('lex-auto-feats',lexAutoFeatures),
            ('word-gram-count',KLUEwordgrams),
            ('stem-gram-count',KLUEstems),
            ('negate-feats',negateCounts),
            ('pos-count',posCounts),
            ('cmu-cluster',cmuClusterFeatures),
            ('all-caps-count',allCapsCount),
            ('hashtags-count',hashTagCount),
            ('elong-count',elongatedWordCount),
            ('punctuation-feats',puncFeatures),
            ('emoti-feats',emotiFeatures),
            ('klue-token-count', KLUEtokenCount),
            ('klue-polarity', KLUEpolarity),
            ('klue-emoti-acro', KLUEemotiacro),
            ]) 
clfpipeline = Pipeline([\
            ('features',features),
            ('clf',LogisticRegression(penalty = 'l2',C = .25))])
#^^^^^^^^^^^^^^^^^BASELINE^^^^^^^^^^^^^^^^^^^^^^^#
wordgrams = Pipeline([\
            ('docs',tran.DocsExtractor(transformedTweetKeyName = 'normalised_string')),\
            ('count',tran.CountVectorizer(tokenizer=string.split,ngram_range=(1, 1) ,binary=True))])
cmuClusterFeatures = Pipeline([\
            ('clusters',tran.ClusterExtractor()),\
            ('count',tran.CountVectorizer(tokenizer=string.split,ngram_range=(1, 1) ,binary=False,\
                     vocabulary = helper.loadJSONfromFile(helper.getProjectPath() + '/wxtalk/resources/lexicons/CMU/CMU-cluster-vocab.json')))])
GUMLTClusterFeatures = Pipeline([\
            ('clusters',tran.ClusterExtractor(['collapsed_token_list','raw_token_list','normalised_token_list'])),\
            ('count',tran.CountVectorizer(tokenizer=string.split,ngram_range=(1, 1) ,binary=False,\
                     vocabulary = helper.loadJSONfromFile(helper.getProjectPath() + '/wxtalk/resources/lexicons/CMU/CMU-cluster-vocab.json')))])   
features = FeatureUnion([
            ('word-gram-count',wordgrams ),
            #('stem-gram-count',KLUEstems),
            #('pos-count',posCounts)
            ('cmu-cluster',GUMLTClusterFeatures),
            ]) 
clf =Pipeline([\
            ('features',features),
            ('clf',LogisticRegression(penalty = 'l1',C = 1.0))])


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


#^^^^^^^^^^^^^^^^^CLASSIFIERS^^^^^^^^^^^^^^^^^^^^^^^#
#TODO: Play with params, and probabilistic params
#NB
clfpipeline = Pipeline([\
            ('features',features),
            ('clf',MultinomialNB())])

#SGD
clfpipeline = Pipeline([\
            ('features',features),
            ('clf',SGDClassifier(alpha=.001,n_iter=1000,penalty='elasticnet'))])
clfpipeline = Pipeline([\
            ('features',features),
            ('clf',SGDClassifier(n_iter=50,penalty = 'l2'))])
clfpipeline = Pipeline([\
            ('features',features),
            ('clf',SGDClassifier(n_iter=50,penalty = 'l1'))])
#Logistic Regression / MaxEnt with KLUE best settings
clfpipeline = Pipeline([\
            ('features',features),
            ('clf',LogisticRegression(penalty = 'l1',C = .2))])
clfpipeline = Pipeline([\
            ('features',features),
            ('clf',LogisticRegression(penalty = 'l2',C = .1))])
clfpipeline = Pipeline([\
            ('features',features),
            ('clf',LogisticRegression(penalty = 'l2',C = 0.15))])
clfpipeline = Pipeline([\
            ('features',features),
            ('clf',LogisticRegression(penalty = 'l2',C = 0.5))])


clf1 =Pipeline([\
            ('features',features),
            ('clf',LogisticRegression(penalty = 'l1',C = 1.0))])
clf2 =Pipeline([\
            ('features',features),
            ('clf',LogisticRegression(penalty = 'l1',C = .3))])
clf3 =Pipeline([\
            ('features',features),
            ('clf',LogisticRegression(penalty = 'l1',C = .5))])
clf4 =Pipeline([\
            ('features',features),
            ('clf',LogisticRegression(penalty = 'l1',C = .7))])
clf5 =Pipeline([\
            ('features',features),
            ('clf',LogisticRegression(penalty = 'l1',C = .9))])
clfs= [clf1,clf2,clf3,clf4,clf5]
#random_forest
clfpipeline = Pipeline([\
            ('features',features),
            ('clf',RandomForestClassifier(n_estimators=10))])
            
#SVM with NRC 2013 settings ---NOTE: No luck with results so far it always predicts neautral
clfpipeline = Pipeline([\
            ('features',features),
            ('clf',SVC(C=.005,kernel='linear',probability=False))])
#clfpipeline = Pipeline([\
#            ('features',features),
#            ('clf',SVC(C=.5,kernel='linear',probability=False))])
            
clfpipeline = Pipeline([\
            ('features',features),
            ('clf',LinearSVC(C=.55))])

