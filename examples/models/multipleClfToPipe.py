#AUTHOR: Steven Zimmerman
#Date: 11-JUN-2015

#Example to create a list of classifiers with short name then iterate over this list to produce
#metrics. e.g. f1 and precision
#NOTE: The classifiers must be able to accept sparse matrices in this examples
#A short list of these is found at: https://www.kaggle.com/c/amazon-employee-access-challenge/forums/t/5128/scikit-learn-models-compatible-with-sparse-matrix/38925

#for all examples
from wxtalk.models import transformers as tran
from wxtalk import helper

import string

from sklearn.pipeline import (Pipeline,FeatureUnion)
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import (CountVectorizer, TfidfTransformer, TfidfVectorizer)
from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier

import sklearn.externals.joblib as joblib

clfList = [['SGD',SGDClassifier()],['MultiNB',MultinomialNB()],['Random Forest',RandomForestClassifier()]]

#PIPELINE SETUP
ngramCountPipe = Pipeline([\
            ('docs',tran.DocsExtractor()),\
            ('count',tran.CountVectorizer(analyzer=string.split))])

ngramTfidfPipe = Pipeline([\
            ('docs',tran.DocsExtractor()),\
            ('tf-idf',tran.TfidfVectorizer(analyzer=string.split))])

otherFeaturesPipe = Pipeline([\
            ('text-feats-dict',tran.TextFeaturesExtractor(keysToDrop=['urloremail_present',"hashtag_present"])),\
            ('text-feats-vec',tran.DictVectorizer())])

features = FeatureUnion([
            ('ngrams',ngramCountPipe),
            ('others',otherFeaturesPipe)])

def produceClfResults(clfName, clf):
    '''Provide name string of clf and clf, will produce models and print evalua results'''
    clfpipeline = Pipeline([\
                ('features',features),
                ('clf',clf)])
                
    
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
    #TODO: Add in confusion matrix --> vvvv
    #       from sklearn.metrics import confusion_matrix
    #       self.confusionMatrix = confusion_matrix(self.Y_set,y_pred)
    loadedpipe = joblib.load('../../wxtalk/resources/data/pickles/test.pkl')
    #dev
    inFile = '../../wxtalk/resources/data/SemEval/SemDevTriples.json'
    data = helper.loadJSONfromFile(inFile)           
    ed = tran.TriplesYsExtractor()
    triplesList, expected_ys = ed.transform(data,ysKeyName = 'sentiment_num')
    predicted_ys = loadedpipe.predict(triplesList)
    print "Results for model = " + clfName
    print helper.evaluateResults(expected_ys,predicted_ys)


#example:    
for item in clfList:
    produceClfResults(item[0],item[1])

