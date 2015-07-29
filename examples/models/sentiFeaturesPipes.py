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

print "Hash normal"
testingPipe(clfpipeline,ysKeyName='sentiment_num',userNorm = None,urlNorm = None,hashNormalise=True,digitNormalise=False)
print "Digits normal"
testingPipe(clfpipeline,ysKeyName='sentiment_num',userNorm = None,urlNorm = None,hashNormalise=False,digitNormalise=True)
print "Hash and digits normal"
testingPipe(clfpipeline,ysKeyName='sentiment_num',userNorm = None,urlNorm = None,hashNormalise=True,digitNormalise=True)

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


features = Pipeline([\
            ('docs',tran.DocsExtractor(transformedTweetKeyName = 'normalised_string')),\
            ('count',tran.CountVectorizer(tokenizer=string.split,ngram_range=(1, 1) ,binary=True))])
clf1 =Pipeline([\
            ('features',features),
            ('clf',LogisticRegression(penalty = 'l2',C = 1.0))])
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

#^^^^^^^^^^^^^^^^^TESTING PIPELINE^^^^^^^^^^^^^^^^^^^^^^^#
def testingPipe(clfpipeline,ysKeyName='sentiment_num',userNorm = None,urlNorm = None,hashNormalise=False,digitNormalise=False):  #options -->         'sentiment_num',"neg_bool","neut_bool","pos_bool"
    #1d - full pipeline with dump of model to pickle and then reload and predict on unseen data
    print "Building Model"
    inFile = '../../wxtalk/resources/data/SemEval/SemTrainTriples.json'
    data = helper.loadJSONfromFile(inFile)           
    ed = tran.TweetTransformer(userNorm = userNorm,urlNorm = urlNorm,hashNormalise=hashNormalise,digitNormalise=digitNormalise)
    tweetsList, ysList = ed.transform(data,ysKeyName = ysKeyName)
    clfpipeline.fit(tweetsList,ysList)
    joblib.dump(clfpipeline, '../../wxtalk/resources/data/pickles/test.pkl') 
    loadedpipe = joblib.load('../../wxtalk/resources/data/pickles/test.pkl')
    
    #1e - predict on dev/test data and output precision, recall f1
    '''Must complete steps in 1d  and load clfpipeline first'''
    ### DEV 2015
    inFile = '../../wxtalk/resources/data/SemEval/SemDevTriples.json'
    data = helper.loadJSONfromFile(inFile)           
    ed = tran.TweetTransformer(userNorm = userNorm,urlNorm = urlNorm,hashNormalise=hashNormalise,digitNormalise=digitNormalise)
    tweetsList, expected_ys = ed.transform(data,ysKeyName = ysKeyName)
    predicted_ys = loadedpipe.predict(tweetsList)
    print "Results DEV 2015"
    print helper.evaluateResults(expected_ys,predicted_ys)
    
#    ### TEST 2015
#    inFile = '../../wxtalk/resources/data/SemEval/SemTestTriples.json'
#    data = helper.loadJSONfromFile(inFile)           
#    ed = tran.TweetTransformer()
#    tweetsList, expected_ys = ed.transform(data,ysKeyName = ysKeyName)
#    predicted_ys = loadedpipe.predict(tweetsList)
#    print "Results TEST 2015"
#    print helper.evaluateResults(expected_ys,predicted_ys)
#    
#    ### TEST 2013
#    inFile = '../../wxtalk/resources/data/SemEval/SemTest2013Triples.json'
#    data = helper.loadJSONfromFile(inFile)           
#    ed = tran.TweetTransformer(userNorm = userNorm,urlNorm = urlNorm,hashNormalise=hashNormalise,digitNormalise=digitNormalise)
#    tweetsList, expected_ys = ed.transform(data,ysKeyName = ysKeyName)
#    predicted_ys = loadedpipe.predict(tweetsList)
#    print "Results TEST 2013"
#    print helper.evaluateResults(expected_ys,predicted_ys)
    print "Writing to goldstandard"
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
    #helper.dumpJSONtoFile(outFile,data) 
    print "Done"

#^^^^^^^^^^^^^^^Train/Dev --> Test 2015^^^^^^^^^^^^^^^^^^^^^^^^^^^^
def finalTest(clfpipeline,ysKeyName = 'sentiment_num',userNorm = None,urlNorm = None,hashNormalise=False,digitNormalise=False):
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
#    #PREDICT ON TEST 2015
#    ## TEST 2015
#    inFile = '../../wxtalk/resources/data/SemEval/SemTest2015Triples.json'
#    data = helper.loadJSONfromFile(inFile)           
#    ed = tran.TweetTransformer()
#    tweetsList, expected_ys = ed.transform(data,ysKeyName = ysKeyName)
#    predicted_ys = loadedpipe.predict(tweetsList)
#    print helper.evaluateResults(expected_ys,predicted_ys)
    
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
    helper.dumpJSONtoFile(outFile,data) 
    print "Done"

#^^^^^^^^^^^^^^^^^^^^GRIDSEARCH^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
### TEST 2015
inFile = '../../wxtalk/resources/data/SemEval/SemTrainTriples.json'
data = helper.loadJSONfromFile(inFile)           
ed = tran.TweetTransformer(userNorm = None,urlNorm = None,hashNormalise=False,digitNormalise=False)
tweetsList, ysList = ed.transform(data,ysKeyName = 'sentiment_num')
### DEV 2015
inFile = '../../wxtalk/resources/data/SemEval/SemDevTriples.json'
data = helper.loadJSONfromFile(inFile)           
ed = tran.TweetTransformer(userNorm = None,urlNorm = None,hashNormalise=False,digitNormalise=False)
tweetsListDev, expected_ysDev = ed.transform(data,ysKeyName = 'sentiment_num')

##Combine into one train set and build model
#tweetsList.extend(tweetsListDev), ysList.extend(expected_ysDev)
#clfpipeline = Pipeline([\
#            ('features',features),
#            ('clf',SGDClassifier())])
#parameters = {
#    'clf__alpha': (0.00001, 0.000001),
#    'clf__penalty': ('l1','l2', 'elasticnet'),
#    'clf__n_iter': (10, 50, 80),
#}

clfpipeline = Pipeline([\
            ('features',features),
            ('clf',LogisticRegression(penalty='l2'))])
            
parameters = {
    'clf__C': (.5,.4,.3,.2,.1),
#
}
#clfpipeline = Pipeline([\
#            ('features',features),
#            ('clf',SVC())])
#parameters = {
#    'clf__C': (.6,.5,.4,.3,.2),
#    'clf__kernel': ('linear'),
#}

#clfpipeline = Pipeline([\
#            ('features',features),
#            ('clf',LogisticRegression())])
#parameters = {
#    'clf__C': (5.0,.5,.05,.005),
#    'clf__penalty': ('l1','l2'),
#    'clf__multi_class' : ('ovr', 'multinomial')
#}

if __name__ == "__main__":
    # multiprocessing requires the fork to happen in a __main__ protected
    # block
    # find the best parameters for both the feature extraction and the
    # classifier
    #example 2a not nested pipe
    grid_search = GridSearchCV(clfpipeline, parameters, n_jobs=-1, verbose=1)
    print("Performing grid search...")
    print("pipeline:", [name for name, _ in clfpipeline.steps])
    print("parameters:")
    pprint(parameters)
    t0 = time()    
    grid_search.fit(tweetsList, ysList)
    print("done in %0.3fs" % (time() - t0))
    print()
    print("Best score: %0.3f" % grid_search.best_score_)
    print("Best parameters set:")
    best_parameters = grid_search.best_estimator_.get_params()
    for param_name in sorted(parameters.keys()):
        print("\t%s: %r" % (param_name, best_parameters[param_name]))       


#------------------live data-------------------------
#1 - Example of Live Data Pipeline --> predict on live Tweets.  Attach prediction/result to each dictionary
'''Assumes that pickle files contain the desired pipeline'''
inFile = '../../wxtalk/resources/data/LiveTweets/LiveCorpus.json'
outFile = '../../wxtalk/resources/data/LiveTweets/LiveCorpusWithTriples.json'
#helper.extractTweetNLPtriples(inFile,outFile)
loadedpipe = joblib.load('../../wxtalk/resources/data/pickles/test.pkl')
inFile = '../../wxtalk/resources/data/LiveTweets/LiveCorpusWithTriples.json'
outFile = '../../wxtalk/resources/data/LiveTweets/LiveCorpusScored.json'
data = helper.loadJSONfromFile(inFile)           
ed = tran.TweetTransformer(userNorm = None,urlNorm = None,hashNormalise=False,digitNormalise=False)
triplesList = ed.transform(data)
predicted_ys = loadedpipe.predict(triplesList)
sentimentList = predicted_ys.tolist()
#TODO: Create a fully working function out of this, needs to be tested
#       Should also have error handling for when counts don't match
#TODO: You could also add in topic classification here e.g. dict["topic_wx"] = topic_wx[count]
count = 0 
for dict in data:
    keydropped = dict.pop("tagged_tweet_triples",None)  #stored as variable in order to supress print to screen
    dict["sentiment_score"] = sentimentList[count]
    count += 1

helper.dumpJSONtoFile(outFile,data)
