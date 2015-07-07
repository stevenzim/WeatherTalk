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
from sklearn.naive_bayes import MultinomialNB


import sklearn.externals.joblib as joblib

#for GridSearchCV examples
from sklearn.grid_search import GridSearchCV
#from __future__ import print_function
from pprint import pprint
from time import time
import logging



#EXAMPLE 0 - Extract NLP Triples
#0a - semeval data
inFile = '../../wxtalk/resources/data/Kaggle/train.json'
outFile = '../../wxtalk/resources/data/Kaggle/trainTriples.json'
helper.extractTweetNLPtriples(inFile,outFile)


inFile = '../../wxtalk/resources/data/Kaggle/test.json'
outFile = '../../wxtalk/resources/data/Kaggle/testTriples.json'
helper.extractTweetNLPtriples(inFile,outFile)

#0b - live tweets
#single file
#inFile = '../../wxtalk/resources/data/LiveTweets/LiveTweets.json'
#outFile = '../../wxtalk/resources/data/LiveTweets/LiveTweetsTriples.json'
#helper.extractTweetNLPtriples(inFile,outFile)


#EXAMPLE 1 - MY FIRST PIPELINE WITH FEATURE UNION
#Parameters entered in below are suggested by grid_search
ngramCountPipe = Pipeline([\
            ('docs',tran.DocsExtractor()),\
            ('count',tran.CountVectorizer(analyzer=string.split,max_df= 0.75,max_features=50000,ngram_range=(1, 1) ))])


clfpipeline = Pipeline([\
            ('count',ngramCountPipe),
            ('clf',SGDClassifier(alpha=1e-05,n_iter=50,penalty='elasticnet'))])
            
           

clfpipeline = Pipeline([\
            ('count',ngramCountPipe),
            ('clf',MultinomialNB())])
            
            
ngramTfidfPipe = Pipeline([\
            ('docs',tran.DocsExtractor()),\
            ('tf-idf',tran.TfidfVectorizer(analyzer=string.split,norm = 'l2',use_idf= False))])

clfpipeline = Pipeline([\
            ('tf-idf',ngramTfidfPipe),
            ('clf',SGDClassifier(alpha=1e-05,n_iter=50,penalty='elasticnet'))])


clfpipeline = Pipeline([\
            ('count',ngramTfidfPipe),
            ('clf',MultinomialNB())])

otherFeaturesPipe = Pipeline([\
            ('text-feats-dict',tran.TextFeaturesExtractor(keysToDrop=[])),\
            #('text-feats-dict',tran.TextFeaturesExtractor(keysToDrop=['urloremail_present',"hashtag_present"])),\
            ('text-feats-vec',tran.DictVectorizer())])

features = FeatureUnion([
            ('ngrams',ngramCountPipe),
            ('others',otherFeaturesPipe)])

clfpipeline = Pipeline([\
            ('features',features),
            ('clf',SGDClassifier(alpha=1e-05,n_iter=50,penalty='elasticnet'))])




#1d - full pipeline with dump of model to pickle and then reload and predict on unseen data
inFile = '../../wxtalk/resources/data/Kaggle/trainTriples.json'
data = helper.loadJSONfromFile(inFile)           
ed = tran.TriplesYsExtractor()
triplesList, ysList = ed.transform(data,ysKeyName = "topic_wx_00")
clfpipeline.fit(triplesList,ysList)
joblib.dump(clfpipeline, '../../wxtalk/resources/data/Kaggle/pickles/kaggle-proto.pkl') 
loadedpipe = joblib.load('../../wxtalk/resources/data/Kaggle/pickles/kaggle-proto.pkl')

#1e - predict on dev/test data and output precision, recall f1
'''Must complete steps in 1d  and load clfpipeline first'''
#TODO: Add in confusion matrix --> vvvv
#       from sklearn.metrics import confusion_matrix
#       self.confusionMatrix = confusion_matrix(self.Y_set,y_pred)
loadedpipe = joblib.load('../../wxtalk/resources/data/Kaggle/pickles/kaggle-proto.pkl')
#test
inFile = '../../wxtalk/resources/data/Kaggle/testTriples.json'
data = helper.loadJSONfromFile(inFile)           
ed = tran.TriplesYsExtractor()
triplesList, expected_ys = ed.transform(data,ysKeyName = "topic_wx_00")
predicted_ys = loadedpipe.predict(triplesList)
print helper.evaluateResults(expected_ys,predicted_ys)




#1f - Example of Live Data Pipeline --> predict on live Tweets.  Attach prediction/result to each dictionary
#     YIPPPEEE!!!! It works
'''Assumes that pickle files contain the desired pipeline'''
#inFile = '../../wxtalk/resources/data/Kaggle/liveTweets.json'
#outFile = '../../wxtalk/resources/data/Kaggle/liveTriples.json'
#helper.extractTweetNLPtriples(inFile,outFile)
loadedpipe = joblib.load('../../wxtalk/resources/data/Kaggle/pickles/kaggle-proto.pkl')
inFile = '../../wxtalk/resources/data/Kaggle/liveTriples.json'
outFile = '../../wxtalk/resources/data/Kaggle/liveTweetsScored.json'
data = helper.loadJSONfromFile(inFile)           
ed = tran.TriplesYsExtractor()
triplesList = ed.transform(data)
predicted_ys = loadedpipe.predict(triplesList)
sentimentList = predicted_ys.tolist()
#TODO: Create a fully working function out of this, needs to be tested
#       Should also have error handling for when counts don't match
#TODO: You could also add in topic classification here e.g. dict["topic_wx"] = topic_wx[count]
count = 0 
for dict in data:
    keydropped = dict.pop("tagged_tweet_triples",None)  #stored as variable in order to supress print to screen
    dict["topic_wx_score"] = sentimentList[count]
    count += 1

helper.dumpJSONtoFile(outFile,data)   #dump live tweets with classifer predictions added to json





#Create corpus
kaggleFile = '../../wxtalk/resources/data/Kaggle/train.json'
kaggleThousandFile = '../../wxtalk/resources/data/Kaggle/thousand-train.json'
kaggle = helper.loadJSONfromFile(kaggleFile)
combinedFile = '../../wxtalk/resources/data/Kaggle/combined.json'
liveThousandFile = liveFile = '../../wxtalk/resources/data/Kaggle/liveTweetsScored.json'
liveScored = helper.loadJSONfromFile(liveFile)

subKaggle = []
for item in kaggle:
    if item["s5_conf"] < 0.000001:
        item["topic_wx_score"] = True
        subKaggle.append(item)


subLive = []
for item in liveScored:
    if item["topic_wx_score"] == False:
        subLive.append(item)

subPos = subKaggle[:1000]
subPos.extend(subLive[:1000])
helper.dumpJSONtoFile(combinedFile,subPos)





#1d - full pipeline with dump of model to pickle and then reload and predict on unseen data
#inFile = '../../wxtalk/resources/data/Kaggle/combined.json'

inFile = '../../wxtalk/resources/data/Kaggle/combinedTriples.json'
#helper.extractTweetNLPtriples(inFile,outFile)
data = helper.loadJSONfromFile(inFile)           
ed = tran.TriplesYsExtractor()
triplesList, ysList = ed.transform(data,ysKeyName = "topic_wx_score")
clfpipeline.fit(triplesList,ysList)
joblib.dump(clfpipeline, '../../wxtalk/resources/data/Kaggle/pickles/kaggle-proto.pkl') 
loadedpipe = joblib.load('../../wxtalk/resources/data/Kaggle/pickles/kaggle-proto.pkl')




#1f - Example of Live Data Pipeline --> predict on live Tweets.  Attach prediction/result to each dictionary
#     YIPPPEEE!!!! It works
'''Assumes that pickle files contain the desired pipeline'''
#inFile = '../../wxtalk/resources/data/Kaggle/live2tweets.json'
#outFile = '../../wxtalk/resources/data/Kaggle/live2Triples.json'
#helper.extractTweetNLPtriples(inFile,outFile)
loadedpipe = joblib.load('../../wxtalk/resources/data/Kaggle/pickles/kaggle-proto.pkl')
inFile = '../../wxtalk/resources/data/Kaggle/live2Triples.json'
outFile = '../../wxtalk/resources/data/Kaggle/live2TweetsScored.json'
data = helper.loadJSONfromFile(inFile)           
ed = tran.TriplesYsExtractor()
triplesList = ed.transform(data)
predicted_ys = loadedpipe.predict(triplesList)
sentimentList = predicted_ys.tolist()
#TODO: Create a fully working function out of this, needs to be tested
#       Should also have error handling for when counts don't match
#TODO: You could also add in topic classification here e.g. dict["topic_wx"] = topic_wx[count]
count = 0 
for dict in data:
    keydropped = dict.pop("tagged_tweet_triples",None)  #stored as variable in order to supress print to screen
    dict["topic_wx_score"] = sentimentList[count]
    count += 1

helper.dumpJSONtoFile(outFile,data)   #dump live tweets with classifer predictions added to json

#EXAMPLE 2 - GRIDSEARCH
#Modified version by Steven Zimmerman
# Original from http://scikit-learn.org/stable/_downloads/grid_search_text_feature_extraction.py
# ORIGINAL Authors: Olivier Grisel <olivier.grisel@ensta.org>
#         Peter Prettenhofer <peter.prettenhofer@gmail.com>
#         Mathieu Blondel <mathieu@mblondel.org>
# License: BSD 3 clause


print(__doc__)

# Display progress logs on stdout
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')
                    
#############EXAMPLE 2A
#base data example 2a
inFile = '../../wxtalk/resources/data/SemEval/SemTrainTriples.json'
data = helper.loadJSONfromFile(inFile)           
ed = tran.TriplesYsExtractor()
triplesList, ysList = ed.transform(data,ysKeyName = 'sentiment_num')



# define a pipeline combining a text feature extractor with a simple
# classifier
clfpipeline = Pipeline([
    ('docs', tran.DocsExtractor()),
    ('vec-t', CountVectorizer(analyzer=string.split)),
    ('tfidf', TfidfTransformer()),
    ('clf', SGDClassifier()),
])

# uncommenting more parameters will give better exploring power but will
# increase processing time in a combinatorial way
parameters = {
    #'vect__analyzer':(string.split),
    'vec-t__max_df': (0.5, 0.75, 1.0),
    #'vect__max_features': (None, 5000, 10000, 50000),
    #'vect__ngram_range': ((1, 1), (1, 2)),  # unigrams or bigrams
    #'tfidf__use_idf': (True, False),
    #'tfidf__norm': ('l1', 'l2'),
    #'clf__alpha': (0.00001, 0.000001),
    #'clf__penalty': ('l2', 'elasticnet'),
    #'clf__n_iter': (10, 50, 80),
}


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



#############EXAMPLE 2B
#params and data example 2b nested params
inFile = '../../wxtalk/resources/data/SemEval/SemTrainTriples.json'
data = helper.loadJSONfromFile(inFile)           
ed = tran.TriplesYsExtractor()
triplesList, ysList = ed.transform(data,ysKeyName = 'sentiment_num')
y10=ysList[0:10]
t10 = triplesList[0:10]

#simplepipe
nestedpipeline= Pipeline([('text-feats-dict',tran.TextFeaturesExtractor()),\
                    ('text-feats-vec',tran.DictVectorizer()),\
                    ('clf',SGDClassifier())])
nestedparameters = {
    'text-feats-dict__keysToDrop':(['questmark_present'],['urloremail_present'],['questmark_present','urloremail_present'])
}

#complexpipe
nestedpipeline = Pipeline([\
            ('features',FeatureUnion([
                    ('ngrams-idf',Pipeline([\
                                    ('docs',tran.DocsExtractor()),\
                                    ('tf-idf',tran.TfidfVectorizer(analyzer=string.split))])),
                    ('others',Pipeline([\
                                ('text-feats-dict',tran.TextFeaturesExtractor()),\
                                ('text-feats-vec',tran.DictVectorizer())]))])),
            ('clf',SGDClassifier())])
nestedparameters = {'features__others__text-feats-dict__keysToDrop':\
                     [['urloremail_present'],['questmark_present'],[]]}




if __name__ == "__main__":
    # multiprocessing requires the fork to happen in a __main__ protected
    # block
    # find the best parameters for both the feature extraction and the
    # classifier
    #example 2a not nested pipe
    grid_search = GridSearchCV(nestedpipeline, nestedparameters, n_jobs=-1, verbose=1)
    print("Performing grid search...")
    print("pipeline:", [name for name, _ in nestedpipeline.steps])
    print("parameters:")
    pprint(nestedparameters)
    t0 = time()    
    grid_search.fit(t10, y10)
    print("done in %0.3fs" % (time() - t0))
    print()
    print("Best score: %0.3f" % grid_search.best_score_)
    print("Best parameters set:")
    best_parameters = grid_search.best_estimator_.get_params()
    for param_name in sorted(nestedparameters.keys()):
        print("\t%s: %r" % (param_name, best_parameters[param_name]))


#vvvvvvvvvvvvOTHER USEFUL EXAMPLESvvvvvvvvvvv
# X = any aribitrary corpus in list format
inFile = '../../wxtalk/resources/data/SemEval/SemTrainTriples.json'
data = helper.loadJSONfromFile(inFile)  
ed = tran.TriplesYsExtractor()
triplesList = ed.transform(data)
extractor = tran.DocsExtractor()
X = extractor.transform(triplesList)
X = X[:3] #take first 3

#simple string split on corpus to learn dictionary
#dictionary is then dumped to json
vectorizer =  CountVectorizer(analyzer=string.split, min_df=1) #string.split is a trick mentioned in scikit section4.2.3.10.
unigrams  = vectorizer.fit_transform(X)
vocab = vectorizer.vocabulary_
helper.dumpJSONtoFile('../../wxtalk/resources/data/SemEval/SemEvalVocabulary.json',vocab)

#TFidf vectorizer
vectorizer =  TfidfVectorizer(analyzer=string.split, min_df=1) #string.split is a trick mentioned in scikit section4.2.3.10.
unigrams  = vectorizer.fit_transform(X)
vocab = vectorizer.vocabulary_


#load vocabulary from json file
#necessary to vectorize unseen data
vocabFile = '../../wxtalk/resources/data/SemEval/SemEvalVocabulary.json'
vocab = helper.loadJSONfromFile(vocabFile)
vectorizer =  CountVectorizer(analyzer=string.split, min_df=1,\
                vocabulary = vocab) 
X2 = X
X2.append('happy happy :) :) no') #append a new unseen example
unigrams  = vectorizer.fit_transform(X2)
unigrams.toarray()  #now you will see added on vector with new word counts, still with original dictionary


