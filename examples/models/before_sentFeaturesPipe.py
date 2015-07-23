#for all examples
from wxtalk.modelbuilder import z_transformers as tran
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

#wordGramCount = Pipeline([\
#            ('docs',tran.DocsExtractor()),\
#            ('count',tran.CountVectorizer(tokenizer=string.split,max_df= 0.75,max_features=50000,ngram_range=(1, 1) ,binary=False))])

wordGramCount = Pipeline([\
            ('docs',tran.DocsExtractor()),\
            ('count',tran.CountVectorizer(tokenizer=string.split,ngram_range=(1, 4) ,binary=True,min_df=5))])                 

NRCwordgrams = Pipeline([\
            ('docs',tran.DocsExtractor()),\
            ('count',tran.CountVectorizer(tokenizer=string.split,ngram_range=(1, 4) ,binary=True,min_df=5))])  
     
#char-grams
#TODO: Waiting to hear back from authors regarding window position, is accross entire tweet or individual words
#TODO: investigate options for ngram range (they use 3,5 in paper)
#charGramCount = Pipeline([\
#            ('docs',tran.DocsExtractor()),\
#            ('count',tran.CountVectorizer(analyzer='char',max_df= 0.75,max_features=50000,ngram_range=(3, 3) ))])
NRCchargrams = Pipeline([\
            ('docs',tran.DocsExtractor()),\
            ('count',tran.CountVectorizer(tokenizer=string.split,analyzer='char',ngram_range=(3, 5) ,binary=True,min_df=5))])

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
cmuClusterFeatures = Pipeline([\
            ('clusters',tran.ClusterExtractor()),\
            ('count',tran.CountVectorizer(tokenizer=string.split,ngram_range=(1, 1) ,binary=False,\
                     vocabulary = helper.loadJSONfromFile(helper.getProjectPath() + '/wxtalk/resources/lexicons/CMU/CMU-cluster-vocab.json')))])    


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
#RTRGO/prototype
rtrgoFeatures = Pipeline([\
            ('text-feats-dict',tran.TextFeaturesExtractor(keysToDrop=[])),\
            ('text-feats-vec',tran.DictVectorizer())])
#KLUE
KLUEwordgrams = Pipeline([\
            ('docs',tran.DocsExtractor(hashNormalise=False)),\
            ('count',tran.CountVectorizer(tokenizer=string.split,ngram_range=(1, 2) ,binary=True,min_df=5))])

KLUEstems = Pipeline([\
            ('docs',tran.DocsExtractor()),\
            ('stems',tran.StemExtractor()),\
            ('count',tran.CountVectorizer(tokenizer=string.split,ngram_range=(1, 2) ,binary=True,min_df=5))])

KLUEtokenCount = Pipeline([\
            ('token-count-dict',tran.TokenCountExtractor()),\
            ('token-count-vec',tran.DictVectorizer())])
            
KLUEpolarity = Pipeline([\
            ('polarity-dict',tran.KLUEpolarityExtractor('klue-afinn')),\
            ('polarity-vec',tran.DictVectorizer())])
#KLUEpolarity = Pipeline([\
#            ('docs',tran.DocsExtractor(hashNormalise=False)),\
#            ('polarity-dict',tran.KLUEpolarityExtractor('klue-afinn')),\
#            ('polarity-vec',tran.DictVectorizer())])

KLUEemotiacro = Pipeline([\
            ('emoti-acro-dict',tran.KLUEpolarityExtractor('klue-both')),\
            ('emoti-acro-vec',tran.DictVectorizer())])            
#KLUEemotiacro = Pipeline([\
#            ('docs',tran.DocsExtractor(hashNormalise=False)),\
#            ('emoti-acro-dict',tran.KLUEpolarityExtractor('klue-both')),\
#            ('emoti-acro-vec',tran.DictVectorizer())])
#KLUE features
features = FeatureUnion([
            ('word-gram-count',KLUEwordgrams),
            #('stem-gram-count',KLUEstems),
            ('negate-feats',negateCounts),
            #('pos-count',posCounts),
            #('cmu-cluster',cmuClusterFeatures),
            #('all-caps-count',allCapsCount),
            #('hashtags-count',hashTagCount),
            #('elong-count',elongatedWordCount),
            #('punctuation-feats',puncFeatures),
            #('emoti-feats',emotiFeatures),
            ('klue-token-count', KLUEtokenCount),
            ('klue-polarity', KLUEpolarity),
            ('klue-emoti-acro', KLUEemotiacro),
            #('my-feats',originalFeatures)
            ])
testTweet = helper.loadJSONfromFile('KLUE-1tweet.json')
testTriples = helper.extractTweetNLPtriples('KLUE-1tweet.json')
ed = tran.TriplesYsExtractor(negateTweet=True)
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
            ('docs',tran.DocsExtractor(collapseTweet = True)),\
            ('count',tran.CountVectorizer(tokenizer=string.split,ngram_range=(1, 1) ,binary=True))])
GUMLTstems = Pipeline([\
            ('docs',tran.DocsExtractor(collapseTweet = True)),\
            ('stems',tran.StemExtractor()),\
            ('count',tran.CountVectorizer(tokenizer=string.split,ngram_range=(1, 1) ,binary=True))])
GUMLTpolarity = Pipeline([\
            ('polarity-dict',tran.GUMLTsentiWordNetExtractor()),\
            ('polarity-vec',tran.DictVectorizer())])


#***********My features*************
#TODO: Implement option in lexicons to put score of last polar feature less than 0 and minimum polar score


#^^^^^^^^^^^^^^^^^FEATURE UNION^^^^^^^^^^^^^^^^^^^^^^^#
#NRC features
features = FeatureUnion([
            ('lex-man-feats',lexManualFeatures),
            ('lex-auto-feats',lexAutoFeatures),
            ('word-gram-count',NRCwordgrams),
            ('char-gram-count',NRCchargrams),
            #('negate-feats',negateCounts),
            ('pos-count',posCounts),
            ('cmu-cluster',cmuClusterFeatures),
            #('emoti-cluster',emotiClusterFeatures),
            ('all-caps-count',allCapsCount),
            ('hashtags-count',hashTagCount),
            ('elong-count',elongatedWordCount),
            ('punctuation-feats',puncFeatures),
            ('emoti-feats',emotiFeatures),
            #('feats-other-papers', otherPaperFeatures),
#            ('rtrgo-encode-feats', rtrgoFeatures),
            #('klue-token-count', KLUEtokenCount),
            #('my-feats',originalFeatures)
            ]) 



#GM-MLT features
features = FeatureUnion([
            ('word-gram-count',GUMLTwordGrams),
            ('stem-gram-count',GUMLTstems ),
            ('negate-feats',negateCounts),
            #('pos-count',posCounts),
            ('cmu-cluster',cmuClusterFeatures),
            #('all-caps-count',allCapsCount),
            #('hashtags-count',hashTagCount),
            #('elong-count',elongatedWordCount),
            #('punctuation-feats',puncFeatures),
            #('emoti-feats',emotiFeatures),
            ('gmmlt-polarity', GUMLTpolarity),
            #('my-feats',originalFeatures)
            ])
            
#favourite features
features = FeatureUnion([
            ('lex-man-feats',lexManualFeatures),
            ('lex-auto-feats',lexAutoFeatures),
            ('word-gram-count',KLUEwordgrams),
            ('stem-gram-count',KLUEstems),
            ('negate-feats',negateCounts),
            ('pos-count',posCounts),
            ('cmu-cluster',cmuClusterFeatures),
            #('emoti-cluster',emotiClusterFeatures),
            ('all-caps-count',allCapsCount),
            ('hashtags-count',hashTagCount),
            ('elong-count',elongatedWordCount),
            ('punctuation-feats',puncFeatures),
            ('emoti-feats',emotiFeatures),
            #('feats-other-papers', otherPaperFeatures),
#            ('rtrgo-encode-feats', rtrgoFeatures),
            ('klue-token-count', KLUEtokenCount),
            ('klue-polarity', KLUEpolarity),
            ('klue-emoti-acro', KLUEemotiacro),
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
            ('clf',SGDClassifier(n_iter=50,penalty = 'l2'))])
clfpipeline = Pipeline([\
            ('features',features),
            ('clf',SGDClassifier(n_iter=50,penalty = 'l1'))])
#Logistic Regression / MaxEnt with KLUE best settings
clfpipeline = Pipeline([\
            ('features',features),
            ('clf',LogisticRegression(penalty = 'l1',C = .6))])
clfpipeline = Pipeline([\
            ('features',features),
            ('clf',LogisticRegression(penalty = 'l2',C = .05))])
clfpipeline = Pipeline([\
            ('features',features),
            ('clf',LogisticRegression(penalty = 'l2',C = 0.15))])
clfpipeline = Pipeline([\
            ('features',features),
            ('clf',LogisticRegression(penalty = 'l2',C = 0.5))])


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
def NRCtestingPipeline(clfpipeline,ysKeyName='sentiment_num',negateTweet = True):  #options -->         'sentiment_num',"neg_bool","neut_bool","pos_bool"
    #1d - full pipeline with dump of model to pickle and then reload and predict on unseen data
    print "Building Model"
    inFile = '../../wxtalk/resources/data/SemEval/SemTrainTriples.json'
    data = helper.loadJSONfromFile(inFile)           
    ed = tran.TriplesYsExtractor(negateTweet=negateTweet)
    triplesList, ysList = ed.transform(data,ysKeyName = ysKeyName)
    clfpipeline.fit(triplesList,ysList)
    joblib.dump(clfpipeline, '../../wxtalk/resources/data/pickles/test.pkl') 
    loadedpipe = joblib.load('../../wxtalk/resources/data/pickles/test.pkl')
    
    #1e - predict on dev/test data and output precision, recall f1
    '''Must complete steps in 1d  and load clfpipeline first'''
    ### DEV 2015
    inFile = '../../wxtalk/resources/data/SemEval/SemDevTriples.json'
    data = helper.loadJSONfromFile(inFile)           
    ed = tran.TriplesYsExtractor(negateTweet=negateTweet)
    triplesList, expected_ys = ed.transform(data,ysKeyName = ysKeyName)
    predicted_ys = loadedpipe.predict(triplesList)
    print "Results DEV 2015"
    print helper.evaluateResults(expected_ys,predicted_ys)
    
    ### TEST 2015
    inFile = '../../wxtalk/resources/data/SemEval/SemTestTriples.json'
    data = helper.loadJSONfromFile(inFile)           
    ed = tran.TriplesYsExtractor(negateTweet=negateTweet)
    triplesList, expected_ys = ed.transform(data,ysKeyName = ysKeyName)
    predicted_ys = loadedpipe.predict(triplesList)
    print "Results TEST 2015"
    print helper.evaluateResults(expected_ys,predicted_ys)
    
    ### TEST 2013
    inFile = '../../wxtalk/resources/data/SemEval/SemTest2013Triples.json'
    data = helper.loadJSONfromFile(inFile)           
    ed = tran.TriplesYsExtractor(negateTweet=negateTweet)
    triplesList, expected_ys = ed.transform(data,ysKeyName = ysKeyName)
    predicted_ys = loadedpipe.predict(triplesList)
    print "Results TEST 2013"
    print helper.evaluateResults(expected_ys,predicted_ys)

#^^^^^^^^^^^^^^^^^^^^GRIDSEARCH^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
inFile = '../../wxtalk/resources/data/SemEval/SemTrainTriples.json'
data = helper.loadJSONfromFile(inFile)           
ed = tran.TriplesYsExtractor()
triplesList, ysList = ed.transform(data,ysKeyName = 'sentiment_num')

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
            ('clf',SVC())])
parameters = {
    'clf__C': (5.0,.5,.05,.005),
    'clf__kernel': ('linear','sigmoid'),
}

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
    grid_search.fit(triplesList, ysList)
    print("done in %0.3fs" % (time() - t0))
    print()
    print("Best score: %0.3f" % grid_search.best_score_)
    print("Best parameters set:")
    best_parameters = grid_search.best_estimator_.get_params()
    for param_name in sorted(parameters.keys()):
        print("\t%s: %r" % (param_name, best_parameters[param_name]))       


#^^^^^^^^^^^^^^^Train/Dev --> Test 2015^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#TRAIN 2015
inFile = '../../wxtalk/resources/data/SemEval/SemTrainTriples.json'
data = helper.loadJSONfromFile(inFile)           
ed = tran.TriplesYsExtractor()
triplesList, ysList = ed.transform(data,ysKeyName = 'sentiment_num')
### DEV 2015
inFile = '../../wxtalk/resources/data/SemEval/SemDevTriples.json'
data = helper.loadJSONfromFile(inFile)           
ed = tran.TriplesYsExtractor()
triplesListDev, expected_ysDev = ed.transform(data,ysKeyName = 'sentiment_num')

#Combine into one train set and build model
triplesList.extend(triplesListDev), ysList.extend(expected_ysDev)
clfpipeline.fit(triplesList,ysList)
joblib.dump(clfpipeline, '../../wxtalk/resources/data/pickles/test.pkl') 
loadedpipe = joblib.load('../../wxtalk/resources/data/pickles/test.pkl')

#PREDICT ON TEST 2015
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
print "Results TEST 2013"
print helper.evaluateResults(expected_ys,predicted_ys)

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

goldFile = open('gold2013.tsv','w')
predFile = open('pred2103.tsv','w')

strScore = lambda score: "negative" if (score == -1) else ("positive" if (score == 1) else "neutral")
for dict in data:
    goldFile.write(dict["tweet_id"] + '\t' + dict["semeval_id"] + '\t' + dict["sentiment_orig"] + '\t' + dict["text"] + '\n')
    predFile.write(dict["tweet_id"] + '\t' + dict["semeval_id"] + '\t' + strScore(dict["sentiment_score"]) + '\t' + dict["text"] + '\n')

goldFile.close()
predFile.close()
helper.dumpJSONtoFile(outFile,data) 
