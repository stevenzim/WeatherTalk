#for all examples
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


NRCwordgrams = Pipeline([\
            ('docs',tran.DocsExtractor()),\
            ('count',tran.CountVectorizer(tokenizer=string.split,ngram_range=(1, 4) ,binary=True,min_df=1))])  
     
#char-grams
#NRCchargrams = Pipeline([\
#            ('docs',tran.DocsExtractor('normalised_string')),\
#            ('count',tran.CountVectorizer(tokenizer=string.split,analyzer='char',ngram_range=(3, 5) ,binary=True,min_df=1))])
NRCchargrams = Pipeline([\
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
            ('negate-feats',negateCounts)
            ]) 
clfpipeline = Pipeline([\
            ('features',features),
            ('clf',LogisticRegression(penalty = 'l2',C = .5))])

#**********Other papers features***
#TODO: Decide which ones, very much like the features from KLUE paper
#RTRGO/prototype
#rtrgoFeatures = Pipeline([\
#            ('text-feats-dict',tran.TextFeaturesExtractor(keysToDrop=[])),\
#            ('text-feats-vec',tran.DictVectorizer())])
#KLUE
KLUEwordgrams = Pipeline([\
            ('docs',tran.DocsExtractor('negated_string')),\
            ('count',tran.CountVectorizer(tokenizer=string.split,ngram_range=(1, 2) ,binary=True,min_df=1))])

negateCounts = Pipeline([\
            ('negate-counts-dict',tran.NegationCountExtractor()),\
            ('negate-vec',tran.DictVectorizer())])
            

KLUEtokenCount = Pipeline([\
            ('token-count-dict',tran.TokenCountExtractor()),\
            ('token-count-vec',tran.DictVectorizer())])
            
KLUEpolarity = Pipeline([\
            ('polarity-dict',tran.KLUEpolarityExtractor('klue-afinn',tokenListKeyName= 'normalised_token_list')),\
            ('polarity-vec',tran.DictVectorizer())])

KLUEemotiacro = Pipeline([\
            ('emoti-acro-dict',tran.KLUEpolarityExtractor('klue-both',tokenListKeyName= 'normalised_token_list')),\
            ('emoti-acro-vec',tran.DictVectorizer())])            

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
            ('clf',LogisticRegression(penalty = 'l2',C = 0.05))])
            
testTweet = helper.loadJSONfromFile('KLUE-1tweet.json')
testTweets = helper.extractTweetNLPtriples('KLUE-1tweet.json')
ed = tran.TweetTransformer(negateTweet=True)
testTriplesList = ed.transform(testTriples) 
testFeatureExtract = features.fit_transform(testTriplesList) 
    
KLUEwordgrams.fit_transform(testTriplesList) 
wordGramTest = ['your not_neg happy_neg :(_neg ']
vectorizer = tran.CountVectorizer(tokenizer=string.split,ngram_range=(1, 2) ,binary=True,min_df=1)
wordgrams  = vectorizer.fit_transform(wordGramTest)
vectorizer.vocabulary_
KLUEstems.fit_transform(testTriplesList) 
KLUEtokenCount.fit_transform(testTriplesList) 
KLUEpolarity.fit_transform(testTriplesList) 
KLUEemotiacro.fit_transform(testTriplesList)  
#----------------            
#GU-MLT
GUMLTwordGrams = Pipeline([\
            ('docs',tran.DocsExtractor(transformedTweetKeyName = 'negated_string')),\
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
             ('clf',LogisticRegression(penalty = 'l2',C = 0.15))])
#finalTest(clfpipeline,digitNormalise=True)




#^^^^^^^^^^^^^^^^^TESTING PIPELINE^^^^^^^^^^^^^^^^^^^^^^^#
def testingPipe(clfpipeline,ysKeyName='sentiment_num',userNorm = None,urlNorm = None,hashNormalise=False,digitNormalise=False):  #options -->         'sentiment_num',"neg_bool","neut_bool","pos_bool"
    #TRAIN MODEL ON TRAINING SET
    print "Building Model"
    inFile = '../../wxtalk/resources/data/SemEval/SemTrainTriples.json'
    data = helper.loadJSONfromFile(inFile)           
    ed = tran.TweetTransformer(userNorm = userNorm,urlNorm = urlNorm,hashNormalise=hashNormalise,digitNormalise=digitNormalise)
    tweetsList, ysList = ed.transform(data,ysKeyName = ysKeyName)
    clfpipeline.fit(tweetsList,ysList)
    joblib.dump(clfpipeline, '../../wxtalk/resources/data/pickles/test.pkl') 
    loadedpipe = joblib.load('../../wxtalk/resources/data/pickles/test.pkl')
    
    #PREDICT ON DEV SET
    '''Must complete steps in 1d  and load clfpipeline first'''
    ### DEV 2015
    inFile = '../../wxtalk/resources/data/SemEval/SemDevTriples.json'
    data = helper.loadJSONfromFile(inFile)           
    ed = tran.TweetTransformer(userNorm = userNorm,urlNorm = urlNorm,hashNormalise=hashNormalise,digitNormalise=digitNormalise)
    tweetsList, expected_ys = ed.transform(data,ysKeyName = ysKeyName)
    predicted_ys = loadedpipe.predict(tweetsList)
    print "Results DEV 2015"
    print helper.evaluateResults(expected_ys,predicted_ys)
    
    print "Writing to goldstandard and prediction files for scoring"
    sentimentList = predicted_ys.tolist()
    count = 0 
    for dict in data:
        keydropped = dict.pop("tagged_tweet_triples",None)  #stored as variable in order to supress print to screen
        dict["sentiment_score"] = sentimentList[count]
        count += 1
    
    goldFile = open('gold-dev13.tsv','w')
    predFile = open('pred-dev13.tsv','w')
    
    strScore = lambda score: "negative" if (score == -1) else ("positive" if (score == 1) else "neutral")
    for dict in data:
        goldFile.write(dict["tweet_id"] + '\t' + dict["semeval_id"] + '\t' + dict["sentiment_orig"] + '\t' + dict["text"] + '\n')
        predFile.write(dict["tweet_id"] + '\t' + dict["semeval_id"] + '\t' + strScore(dict["sentiment_score"]) + '\t' + dict["text"] + '\n')
    
    goldFile.close()
    predFile.close()
    print "Done"

#^^^^^^^^^^^^^^^Train/Dev --> Test 2013^^^^^^^^^^^^^^^^^^^^^^^^^^^^
def finalTest(clfpipeline,ysKeyName = 'sentiment_num',userNorm = None,urlNorm = None,hashNormalise=False,digitNormalise=False):
    '''Combined pipeline for combined Dev/Train datasets to produce final models and model statistics'''
    print "Building Model"
    #TRAIN 2015
    inFile = '../../wxtalk/resources/data/SemEval/SemTrainTriples.json'
    data = helper.loadJSONfromFile(inFile)           
    ed = tran.TweetTransformer(userNorm = userNorm,urlNorm = urlNorm,hashNormalise=hashNormalise,digitNormalise=digitNormalise)
    tweetsList, ysList = ed.transform(data,ysKeyName = ysKeyName)
    ### DEV 2015
    inFile = '../../wxtalk/resources/data/SemEval/SemDevTriples.json'
    data = helper.loadJSONfromFile(inFile)           
    ed = tran.TweetTransformer(userNorm = userNorm,urlNorm = urlNorm,hashNormalise=hashNormalise,digitNormalise=digitNormalise)
    tweetsListDev, expected_ysDev = ed.transform(data,ysKeyName = ysKeyName)
    
    #Combine into one train set and build model
    tweetsList.extend(tweetsListDev), ysList.extend(expected_ysDev)
    clfpipeline.fit(tweetsList,ysList)
    joblib.dump(clfpipeline, '../../wxtalk/resources/data/pickles/model.pkl') 
    loadedpipe = joblib.load('../../wxtalk/resources/data/pickles/model.pkl')
    
    print "Model built, prediction results"

    
    ### TEST 2013
    inFile = '../../wxtalk/resources/data/SemEval/SemTest2013Triples.json'
    data = helper.loadJSONfromFile(inFile)           
    ed = tran.TweetTransformer(userNorm = userNorm,urlNorm = urlNorm,hashNormalise=hashNormalise,digitNormalise=digitNormalise)
    tweetsList, expected_ys = ed.transform(data,ysKeyName = ysKeyName)
    predicted_ys = loadedpipe.predict(tweetsList)
    print "Results TEST 2013"
    print helper.evaluateResults(expected_ys,predicted_ys)
    
    print "preparing gold/predicitons file"
    #output 2013 predictions to file for semeval official scorer
    outFile = '2013-predicitons.json'         
    sentimentList = predicted_ys.tolist()
    #TODO: Create a fully working function out of this, needs to be tested
    #       Should also have error handling for when counts don't match
    #TODO: You could also add in topic classification here e.g. dict["topic_wx"] = topic_wx[count]
    count = 0 
    for dict in data:
        keydropped = dict.pop("tagged_tweet_triples",None)  #stored as variable in order to supress print to screen
        dict["sentiment_score"] = sentimentList[count]
        count += 1
    
    goldFile = open('gold-test13.tsv','w')
    predFile = open('pred-test13.tsv','w')
    
    strScore = lambda score: "negative" if (score == -1) else ("positive" if (score == 1) else "neutral")
    for dict in data:
        goldFile.write(dict["tweet_id"] + '\t' + dict["semeval_id"] + '\t' + dict["sentiment_orig"] + '\t' + dict["text"] + '\n')
        predFile.write(dict["tweet_id"] + '\t' + dict["semeval_id"] + '\t' + strScore(dict["sentiment_score"]) + '\t' + dict["text"] + '\n')
    
    goldFile.close()
    predFile.close()
    print "Done"

