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
#TODO: Waiting for response from authors
# NRC Emotion Lex
# MPQA
# Bing Liu



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
            ('count',tran.CountVectorizer(analyzer=string.split,max_df= 0.75,max_features=50000,ngram_range=(1, 1) ))])
     
#char-grams
#TODO: Waiting to hear back from authors regarding window position, is accross entire tweet or individual words
#TODO: investigate options for ngram range (they use 3,5 in paper)
charGramCount = Pipeline([\
            ('docs',tran.DocsExtractor()),\
            ('count',tran.CountVectorizer(analyzer='char',max_df= 0.75,max_features=50000,ngram_range=(3, 3) ))])


###-------------Negation----------------###
#TODO: Least clear of remaining task, therefor lowest priority
 
            
###--------------POS -------------------###
posCounts = Pipeline([\
            ('lex-feats-dict',tran.POScountExtractor()),\
            ('pos-vec',tran.DictVectorizer())])
            
###---------------clusters--------------###
#CMU 1000
#TODO:

#EMOTICON
#TODO: Use wikipedia per 2013 paper

###---------------encodings-------------###
elongated, emoticons, punctuations,all caps, hashtags
#ALL CAPS
#TODO: The number of words with all chars in upper

#HASH TAGS
#TODO: The number of hashtags

#punctuations
#TODO: Whether the last token contains an exclamation or question mark
#TODO: Lowest priority of ecodings: The # of contiguous seqs of exclamation marks, question marks and both exclamation and question marks

#emoticons
#TODO: get response from authors OPTION --> Use 'E' POS tag to test for presence of emoticon
#TODO: presence or absence of postive and negative emoticons at any position in the tweets
#TODO: whether the last token is a positve or negative emoticon

#elongated words
#TODO: The number of words with one character repeated more than once


#**********Other papers 2 features***
#TODO: Decide which ones, very much like the features from KLUE paper


#***********My features*************
#TODO: Implement option in lexicons to put score of last polar feature less than 0 and minimum polar score


#^^^^^^^^^^^^^^^^^FEATURE UNION^^^^^^^^^^^^^^^^^^^^^^^#
features = FeatureUnion([
            #('lex-man-feats',lexManualfeatures),
            ('lex-auto-feats',lexAutoFeatures),
            ('word-gram-count',wordGramCount),
            ('char-gram-count',charGramCount),
            #('negate-feats',negateFeatures),
            ('pos-count',posCounts),
            #('cmu-cluster',cmuClusterFeatures),
            #('emoti-cluster',emotiClusterFeatures),
            #('all-caps-count',allCapsCount),
            #('hashtags-count',hashTagCount),
            #('punctuation-feats',puncFeatures),
            #('emoti-feats',emotiFeatures),
            #('elong-count',elongatedWordCount),
            #('feats-other-papers', otherPaperFeatures),
            #('my-feats',originalFeatures)
            ]) 

#^^^^^^^^^^^^^^^^^CLASSIFIERS^^^^^^^^^^^^^^^^^^^^^^^#
#TODO: Play with params, and probabilistic params
#NB
#clfpipeline = Pipeline([\
#            ('features',features),
#            ('clf',MultinomialNB())])

#SGD
clfpipeline = Pipeline([\
            ('features',features),
            ('clf',SGDClassifier(alpha=1e-05,n_iter=50,penalty='elasticnet'))])

#Logistic Regression / MaxEnt with KLUE best settings
#clfpipeline = Pipeline([\
#            ('features',features),
#            ('clf',LogisticRegression(penalty = 'l1',C = 0.3))])
            
#^^^^^^^^^^^^^^^^^TESTING PIPELINE^^^^^^^^^^^^^^^^^^^^^^^#
#1d - full pipeline with dump of model to pickle and then reload and predict on unseen data
inFile = '../../wxtalk/resources/data/SemEval/SemTrainTriples.json'
data = helper.loadJSONfromFile(inFile)           
ed = tran.TriplesYsExtractor()
triplesList, ysList = ed.transform(data,ysKeyName = 'sentiment_num')
clfpipeline.fit(triplesList,ysList)
joblib.dump(clfpipeline, '../../wxtalk/resources/data/pickles/test.pkl') 
loadedpipe = joblib.load('../../wxtalk/resources/data/pickles/test.pkl')

#1e - predict on dev/test data and output precision, recall f1
'''Must complete steps in 1d  and load clfpipeline first'''
### DEV 2015
inFile = '../../wxtalk/resources/data/SemEval/SemDevTriples.json'
data = helper.loadJSONfromFile(inFile)           
ed = tran.TriplesYsExtractor()
triplesList, expected_ys = ed.transform(data,ysKeyName = 'sentiment_num')
predicted_ys = loadedpipe.predict(triplesList)
print helper.evaluateResults(expected_ys,predicted_ys)
### TEST 2015
inFile = '../../wxtalk/resources/data/SemEval/SemTestTriples.json'
data = helper.loadJSONfromFile(inFile)           
ed = tran.TriplesYsExtractor()
triplesList, expected_ys = ed.transform(data,ysKeyName = 'sentiment_num')
predicted_ys = loadedpipe.predict(triplesList)
print helper.evaluateResults(expected_ys,predicted_ys)
### TEST 2013
inFile = '../../wxtalk/resources/data/SemEval/SemTest2013Triples.json'
data = helper.loadJSONfromFile(inFile)           
ed = tran.TriplesYsExtractor()
triplesList, expected_ys = ed.transform(data,ysKeyName = 'sentiment_num')
predicted_ys = loadedpipe.predict(triplesList)
print helper.evaluateResults(expected_ys,predicted_ys)
