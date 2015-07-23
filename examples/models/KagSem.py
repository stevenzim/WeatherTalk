#AUTHOR: Steven Zimmerman
#Date: 06-JUL-2015
#References/resources:
#   scikit learn examples - https://github.com/scikit-learn/scikit-learn/tree/master/examples
#                         - http://scikit-learn.org/stable/auto_examples/model_selection/grid_search_text_feature_extraction.html#example-model-selection-grid-search-text-feature-extraction-py
#   Zac Stewart Blog Post - http://zacstewart.com/2014/08/05/pipelines-of-featureunions-of-pipelines.html

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
from sklearn.ensemble import RandomForestClassifier

import sklearn.externals.joblib as joblib

#for GridSearchCV examples
from sklearn.grid_search import GridSearchCV
#from __future__ import print_function
from pprint import pprint
from time import time
import logging



#EXAMPLE 0 - Extract NLP Triples
#0a - semeval data
inFile = '../../wxtalk/resources/data/KagSem/KagSemTrain.json'
outFile = '../../wxtalk/resources/data/KagSem/KagSemTrainTriples.json'
#helper.extractTweetNLPtriples(inFile,outFile)


inFile = '../../wxtalk/resources/data/KagSem/KagSemTest.json'
outFile = '../../wxtalk/resources/data/KagSem/KagSemTestTriples.json'
#helper.extractTweetNLPtriples(inFile,outFile)

#inFile = '../../wxtalk/resources/data/Kaggle/tweetsWxWords.json'
#outFile = '../../wxtalk/resources/data/Kaggle/tweetsWxWordsTriples.json'
#helper.extractTweetNLPtriples(inFile,outFile)

#0b - live tweets
#single file
#inFile = '../../wxtalk/resources/data/LiveTweets/LiveTweets.json'
#outFile = '../../wxtalk/resources/data/LiveTweets/LiveTweetsTriples.json'
#helper.extractTweetNLPtriples(inFile,outFile)


#########################################
#####all features pipeline###############
#########################################

###---------------lexicons-----------###

### -- manual -- ###
# Bing Liu
bingLiu = Pipeline([\
            ('lex-feats-dict',tran.NRCLexiconsExtractor(lexicon = 'BingLiu')),\
            ('lex-feats-vec',tran.DictVectorizer())])

# MPQA
MPQA = Pipeline([\
            ('lex-feats-dict',tran.NRCLexiconsExtractor(lexicon = 'MPQA')),\
            ('lex-feats-vec',tran.DictVectorizer())])

# NRC Emotion Lex
NRCemotion= Pipeline([\
            ('lex-feats-dict',tran.NRCLexiconsExtractor(lexicon = 'NRCemotion')),\
            ('lex-feats-vec',tran.DictVectorizer())])
            
lexManualFeatures = FeatureUnion([
            ('lex-BingLiu-vec',bingLiu),
            ('lex-MPQA-vec',MPQA),
            ('lex-nrcemotion-vec',NRCemotion)])            

### -- automatic -- ###
#NOTE: only unigram and bigram features implemented.  
#TODO: Future work --> Non-contiguous pairs, POS tags, hashtags and all-caps tokens not implement
#                      Furthermore, need to discuss these options with authors as their docs are not clear.

## NRC140 ##
lex140Unis = Pipeline([\
            ('lex-feats-dict',tran.NRCLexiconsExtractor(lexicon = 'NRC140',gramType = 'unigram',tagType = 'token')),\
            ('lex-feats-vec',tran.DictVectorizer())])
lex140Bis = Pipeline([\
            ('lex-feats-dict',tran.NRCLexiconsExtractor(lexicon = 'NRC140',gramType = 'bigram',tagType = 'token')),\
            ('lex-feats-vec',tran.DictVectorizer())])
            
## NRC Hashtag ##

lexHashUnis = Pipeline([\
            ('lex-feats-dict',tran.NRCLexiconsExtractor(lexicon = 'NRCHash',gramType = 'unigram',tagType = 'token')),\
            ('lex-feats-vec',tran.DictVectorizer())])

lexHashBis = Pipeline([\
            ('lex-feats-dict',tran.NRCLexiconsExtractor(lexicon = 'NRCHash',gramType = 'bigram',tagType = 'token')),\
            ('lex-feats-vec',tran.DictVectorizer())])
            

lexAutoFeatures = FeatureUnion([
            ('lex-nrc140-vec',lex140Unis),
            ('lex-nrchash-vec',lexHashUnis),
            ('lex-nrc140-vec',lex140Bis),
            ('lex-nrchash-vec',lexHashBis)])

####---------------n-grams------------------####
#TODO: Investigate options, such as max_df and max_features, perhaps try it with different classifiers
## word-grams
#TODO: Investigate non-contiguous tokens (to time consuming for project, future work)

wordGramCount = Pipeline([\
            ('docs',tran.DocsExtractor()),\
            ('count',tran.CountVectorizer(analyzer=string.split,max_df= 0.75,max_features=50000,ngram_range=(1, 1) ,binary=False))])
#wordGramCount = Pipeline([\
#            ('docs',tran.DocsExtractor()),\
#            ('count',tran.CountVectorizer(analyzer=string.split,ngram_range=(1, 1) ,binary=False))]) 
#            
#wordGramCount = Pipeline([\
#            ('docs',tran.DocsExtractor()),\
#            ('count',tran.CountVectorizer(analyzer=string.split,ngram_range=(1, 4) ,binary=False))])                 
     
#char-grams
#TODO: Waiting to hear back from authors regarding window position, is accross entire tweet or individual words
#TODO: investigate options for ngram range (they use 3,5 in paper)
charGramCount = Pipeline([\
            ('docs',tran.DocsExtractor()),\
            ('count',tran.CountVectorizer(analyzer='char',max_df= 0.75,max_features=50000,ngram_range=(3, 3) ))])
#charGramCount = Pipeline([\
#            ('docs',tran.DocsExtractor()),\
#            ('count',tran.CountVectorizer(analyzer='char',ngram_range=(3, 5) ,binary=True))])

###-------------Negation----------------###
negateCounts = Pipeline([\
            ('negate-counts-dict',tran.negatedSegmentCountExtractor()),\
            ('negate-vec',tran.DictVectorizer())])
 
            
###--------------POS -------------------###
posCounts = Pipeline([\
            ('pos-counts-dict',tran.POScountExtractor()),\
            ('pos-vec',tran.DictVectorizer())])
            
###---------------clusters--------------###
#CMU 1000
#TODO:

#EMOTICON
#TODO: Use wikipedia per 2013 paper

###---------------encodings-------------###
#ALL CAPS
allCapsCount = Pipeline([\
            ('caps-counts-dict',tran.capsCountExtractor()),\
            ('caps-vec',tran.DictVectorizer())])

#HASH TAGS
hashTagCount = Pipeline([\
            ('hashtag-counts-dict',tran.hashCountExtractor()),\
            ('hashtag-vec',tran.DictVectorizer())])

#elongated words
elongatedWordCount = Pipeline([\
            ('elong-counts-dict',tran.elongWordCountExtractor()),\
            ('elong-vec',tran.DictVectorizer())])
#punctuations
puncFeatures = Pipeline([\
            ('punct-features-dict',tran.punctuationFeatureExtractor()),\
            ('punct-vec',tran.DictVectorizer())])

#emoticons
emotiFeatures = Pipeline([\
            ('emoti-features-dict',tran.NRCemoticonExtractor('emoticon')),\
            ('emoti-vec',tran.DictVectorizer())])




#**********Other papers features***
#TODO: Decide which ones, very much like the features from KLUE paper
rtrgoFeatures = Pipeline([\
            ('text-feats-dict',tran.TextFeaturesExtractor(keysToDrop=[])),\
            ('text-feats-vec',tran.DictVectorizer())])

KLUEtokenCount = Pipeline([\
            ('token-count-dict',tran.TokenCountExtractor()),\
            ('token-count-vec',tran.DictVectorizer())])


#***********My features*************
#TODO: Implement option in lexicons to put score of last polar feature less than 0 and minimum polar score


#^^^^^^^^^^^^^^^^^FEATURE UNION^^^^^^^^^^^^^^^^^^^^^^^#
features = FeatureUnion([
            #('lex-man-feats',lexManualFeatures),
            #('lex-auto-feats',lexAutoFeatures),
            ('word-gram-count',wordGramCount),
            ('char-gram-count',charGramCount),
            #('negate-feats',negateCounts),
            ('pos-count',posCounts),
            #('cmu-cluster',cmuClusterFeatures),
            #('emoti-cluster',emotiClusterFeatures),
            ('all-caps-count',allCapsCount),
            ('hashtags-count',hashTagCount),
            ('elong-count',elongatedWordCount),
            ('punctuation-feats',puncFeatures),
            #('emoti-feats',emotiFeatures),
            #('feats-other-papers', otherPaperFeatures),
            #('rtrgo-encode-feats', rtrgoFeatures),
            #('klue-token-count', KLUEtokenCount),
            #('my-feats',originalFeatures)
            ]) 

#^^^^^^^^^^^^^^^^^CLASSIFIERS^^^^^^^^^^^^^^^^^^^^^^^#
#TODO: Play with params, and probabilistic params
#NB
clfpipeline = Pipeline([\
            ('features',features),
            ('clf',MultinomialNB())])

#SGD
clfpipeline = Pipeline([\
            ('features',features),
            ('clf',SGDClassifier(alpha=1e-05,n_iter=50,penalty='elasticnet'))])
clfpipeline = Pipeline([\
            ('features',features),
            ('clf',SGDClassifier(n_iter=10,penalty = 'l2'))])

#Logistic Regression / MaxEnt with KLUE best settings
clfpipeline = Pipeline([\
            ('features',features),
            ('clf',LogisticRegression(penalty = 'l1',C = 0.3))])

#random_forest
clfpipeline = Pipeline([\
            ('features',features),
            ('clf',RandomForestClassifier(n_estimators=10))])
            
#SVM with NRC 2013 settings ---NOTE: No luck with results so far it always predicts neautral
#clfpipeline = Pipeline([\
#            ('features',features),
#            ('clf',SVC(C=.005,kernel='rbf',probability=False))])
clfpipeline = Pipeline([\
            ('features',features),
            ('clf',SVC(C=1.0,kernel='linear',probability=False))])

def testingPipeline():
    #1d - full pipeline with dump of model to pickle and then reload and predict on unseen data
    inFile = '../../wxtalk/resources/data/KagSem/KagSemTrainTriples.json'
    data = helper.loadJSONfromFile(inFile)        
    ed = tran.TriplesYsExtractor()
    triplesList, ysList = ed.transform(data,ysKeyName = "topic_wx_00")
    clfpipeline.fit(triplesList,ysList)
    joblib.dump(clfpipeline, '../../wxtalk/resources/data/KagSem/pickles/kaggle-proto.pkl') 
    loadedpipe = joblib.load('../../wxtalk/resources/data/KagSem/pickles/kaggle-proto.pkl')
    
    #1e - predict on dev/test data and output precision, recall f1
    '''Must complete steps in 1d  and load clfpipeline first'''
    #TODO: Add in confusion matrix --> vvvv
    #       from sklearn.metrics import confusion_matrix
    #       self.confusionMatrix = confusion_matrix(self.Y_set,y_pred)
    loadedpipe = joblib.load('../../wxtalk/resources/data/KagSem/pickles/kaggle-proto.pkl')
    #test
    inFile = '../../wxtalk/resources/data/KagSem/KagSemTestTriples.json'
    data = helper.loadJSONfromFile(inFile)  
    data = removeIdontKnows(data)         
    ed = tran.TriplesYsExtractor()
    triplesList, expected_ys = ed.transform(data,ysKeyName = "topic_wx_00")
    predicted_ys = loadedpipe.predict(triplesList)
    print helper.evaluateResults(expected_ys,predicted_ys)
    
    
    #1f - Example of Live Data Pipeline --> predict on live Tweets.  Attach prediction/result to each dictionary
    #     YIPPPEEE!!!! It works
    '''Assumes that pickle files contain the desired pipeline'''
    #inFile = '../../wxtalk/resources/data/KagSem/liveTweets.json'
    #outFile = '../../wxtalk/resources/data/KagSem/liveTriples.json'
    #helper.extractTweetNLPtriples(inFile,outFile)
    loadedpipe = joblib.load('../../wxtalk/resources/data/KagSem/pickles/kaggle-proto.pkl')
    inFile = '../../wxtalk/resources/data/KagSem/liveTriples.json'
    outFile = '../../wxtalk/resources/data/KagSem/liveTweetsScored.json'
    data = helper.loadJSONfromFile(inFile)           
    ed = tran.TriplesYsExtractor()
    triplesList = ed.transform(data)
    predicted_ys = loadedpipe.predict(triplesList)
    wxPredictList = predicted_ys.tolist()
    #TODO: Create a fully working function out of this, needs to be tested
    #       Should also have error handling for when counts don't match
    #TODO: You could also add in topic classification here e.g. dict["topic_wx"] = topic_wx[count]
    count = 0 
    for dict in data:
        keydropped = dict.pop("tagged_tweet_triples",None)  #stored as variable in order to supress print to screen
        keydropped = dict.pop("coordinates",None)
        keydropped = dict.pop("user",None)
        dict["topic_wx_score"] = wxPredictList[count]
        count += 1
    
    helper.dumpJSONtoFile(outFile,data)   #dump live tweets with classifer predictions added to json








