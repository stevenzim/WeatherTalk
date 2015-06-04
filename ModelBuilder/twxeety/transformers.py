import numpy as np
import string #necessary for analyzer option for feature extractors to split unicode and strings
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import FeatureUnion
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import (CountVectorizer, TfidfTransformer, TfidfVectorizer)
from sklearn.svm import SVC

class TextStats(BaseEstimator, TransformerMixin):
    """Extract features from each document for DictVectorizer"""
    def fit(self, x, y=None):
        return self
    def transform(self, listOftriples):
        return [{'length': len(tripleSetCurrentDoc)} for tripleSetCurrentDoc in listOftriples]


class TextStats(BaseEstimator, TransformerMixin):
    """Extract features from each document for DictVectorizer"""
    def fit(self, x, y=None):
        return self
    def transform(self, listOfTriples):
        return [{'length': len(tripleSetCurrentDoc),\
        'test': len(tripleSetCurrentDoc)} for tripleSetCurrentDoc in listOfTriples]
        #'num_sentences': text.count('.')}

          
def dropKeysVals(listOfDicts, keysToDrop = []):
    '''Remove specified Keys and Values from dictionaries stored in list based 
    on provided list of keysToDrop'''
    #TODO: Perhaps there is a map reduce fucntion that could do this better???
    #       similar to map over in clojure
    #TODO: Perhaps it is less confusing to base it on keys to keep (i.e. features to keep)
    #       vs. keys to drop (i.e. features to drop)
    #TODO: Determine how to pass in list of args to transformers, 
    #       which will then be passed to this function
    if type(keysToDrop) != type([]):
        raise ValueError('keysToDrop must be in a list!')
    #no keys to drop so return full list of dicts
    if len(keysToDrop) == 0:
        return listOfDicts
    #iterate over entire list of dicts --> for each dict iterate over list of keys
    # to drop and drop key --> then add updated dictionary to return list 
    returnList = []
    for dictionary in listOfDicts:
        print dictionary
        for keyName in keysToDrop:
            try:
                dictionary.pop(keyName)
            except:
                raise ValueError('invalid key name in list!')
                continue
        returnList.append(dictionary)
    return returnList             

lod = [{'length': len(tripleSetCurrentDoc),'test': len(tripleSetCurrentDoc)}\
 for tripleSetCurrentDoc in listOfTriples]

               
pipeline = Pipeline([
        #('selector', ItemSelector(key='body')),
        ('stats', TextStats()),  # returns a list of dicts
        ('vect', DictVectorizer()),  # list of dicts -> feature matrix
    ])

import helper
listOfDicts = helper.loadJSONfromFile('data.json')
def getListOfTriples(listOfDicts):
    docsList = []
    triplesList = []
    for dict in listOfDicts:
        docsList.append(dict["normal_string_rtrgo"])
        triplesList.append(dict["tagged_tweet_triples"])
    return docsList,triplesList


listOfDocs,listOfTriples = getListOfTriples(listOfDicts)
        
featureVector = pipeline.fit_transform(listOfTriples)

featureVector.toarray()



class NormalisedDocsList(BaseEstimator, TransformerMixin):
    """Extract normalized string from each document, put into list of docs
     to pass to desired text vectorizer e.g. CountVectorizer or TfidfVectorizer"""
    def fit(self, x, y=None):
        return self
    def transform(self, listOftriples):
        docsList = []
        for tripleSetCurrentDoc in listOftriples:
            tokenList = []
            for triple in tripleSetCurrentDoc:
                token = triple[0]
                #normalising steps some adapted from RTRGO paper
                token = token.lower()
                token = token.replace("#","")
                tokenList.append(token)
            docsList.append(' '.join(tokenList))
        return docsList
            

n = NormalisedDocsList()
n.transform(listOfTriples)




countvecpipe = Pipeline([
        #('selector', ItemSelector(key='body')),
        ('normed-docs', NormalisedDocsList()),  # returns a list of normalised docs e.g. text from doc
        ('count-vect', CountVectorizer()),  # vectorized n-gram counts
    ])

        
countVector = countvecpipe.fit_transform(listOfTriples)

countVector.toarray()

#merge features
featpipe = FeatureUnion([('n-gram-vec',countvecpipe),('feat-vec',pipeline)])








def mergeCSRwithNumpyArrays(csr_array,numpy_array):
    '''
    Inputs 1- csr_matrix (usually a sparse n-gram matrix)
          2- numpy_array(usually non n-gram features)
    Outputs a sparse csr_matrix to be passed into classifiers
    NOTE: must be matching dimensions and must have same dimension
    on concatenating axis'''
    #TODO: If time, throw in error handling
    concatedArray = numpy.concatenate((csr_array.toarray(),numpy_array), axis = 1)
    return csr_matrix(concatedArray)


class Vectorize(object):
    def __init__(self,ngram_range=(1, 1),vocabulary=None,norm='l2'):
        self.countVec =  CountVectorizer(analyzer=string.split, min_df=1,\
                            ngram_range = ngram_range,vocabulary=vocabulary)
        self.tfidfVec =  TfidfVectorizer(analyzer=string.split, min_df=1,\
                            ngram_range = ngram_range,vocabulary=vocabulary,norm=norm)
#countVec =  CountVectorizer(analyzer=string.split, min_df=1,ngram_range=(1, 1),vocabulary=None)        
        self.ngramArray = None
        self.vocabulary = None
     
    def countTransform(self,corpus):
        self.ngramArray = self.countVec.fit_transform(corpus)
        self.vocabulary = self.countVec.vocabulary_
    
    def tfidfTransform(self,corpus):
        self.ngramArray = self.countVec.fit_transform(corpus)
        self.vocabulary = self.countVec.vocabulary_
