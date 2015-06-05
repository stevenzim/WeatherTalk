import numpy as np
import string #necessary for analyzer option for feature extractors to split unicode and strings
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import FeatureUnion
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import (CountVectorizer, TfidfTransformer, TfidfVectorizer)
from sklearn.svm import SVC
import helper


class DocsAndTriplesExtractor(BaseEstimator, TransformerMixin):
    '''Provided a list of dictionaries containing triples created by Twitter NLP
    & normalised strings --> return a document list of string and triples list 
    document list can be passed to tfidfVectorizer for example
    and triples list can be passed to other transformer'''
    def fit(self, x, y=None):
        return self
    def transform(self, listOfDicts ,\
        docsKeyName ="normal_string_rtrgo" , triplesKeyName = "tagged_tweet_triples"):
        docsList = []
        triplesList = []
        for dict in listOfDicts:
            docsList.append(dict[docsKeyName])
            triplesList.append(dict[triplesKeyName])
        return docsList, triplesList

class TextFeaturesExtractor(BaseEstimator, TransformerMixin):
    """Extract features from each document which can then be passed to DictVectorizer
    NOTE: you can pass in list of keys to drop, where key name is representitive of features
    you don't want"""
    #TODO: Verify that when no features returned, that it will still append to other features
    
    def boolTest(self, docTripleSet,tripleIdx,stringToTest):
        '''
        docTripleSet = tripleSet for current document
        tripleIdx --> 0 = token, 1 = POS tag, 2 = confidence
        itemToTest --> Will test if this string exist in current document tokens/POS_TaggedText
        breaks out when True occurs
        '''
        #TODO: change this to re.search and also consider adding functionality for confidence score
        #TODO: optionally consider adding in exception error for confidence score to prevent it from being used
        for triple in docTripleSet:
            if triple[tripleIdx] == stringToTest:
                return True
                break
        return False
            
#        return len(tripleSet)
#     
#                if triple[1] == '#':
#                    self.hashtag_present = True
#                #set url/email feature 
#                if triple[1] == 'U':
#                    self.urloremail_present = True
#                #set question mark feature
#                if triple[0] == '?':
#                    self.questmark_present = True
    def fit(self, x, y=None):
        return self
    def transform(self, listOfTriples, keysToDrop=[]):
        listOfStats = [{'questmark_present': self.boolTest(tripleSetCurrentDoc,0,'?'),\
                    'urloremail_present': self.boolTest(tripleSetCurrentDoc,1,'U'),\
                    "hashtag_present":self.boolTest(tripleSetCurrentDoc,1,'#')}\
                     for tripleSetCurrentDoc in listOfTriples]
        listToReturn = helper.dropKeysVals(listOfStats, keysToDrop)
        return listToReturn


          
#           

#lod = [{'length': len(tripleSetCurrentDoc),'test': len(tripleSetCurrentDoc)}\
# for tripleSetCurrentDoc in listOfTriples]

#               
#pipeline = Pipeline([
#        #('selector', ItemSelector(key='body')),
#        ('stats', TextStats()),  # returns a list of dicts
#        ('vect', DictVectorizer()),  # list of dicts -> feature matrix
#    ])


#listOfDicts = helper.loadJSONfromFile('data.json')


#def getListOfTriples(listOfDicts):
#    docsList = []
#    triplesList = []
#    for dict in listOfDicts:
#        docsList.append(dict["normal_string_rtrgo"])
#        triplesList.append(dict["tagged_tweet_triples"])
#    return docsList,triplesList


#listOfDocs,listOfTriples = getListOfTriples(listOfDicts)
#        
#featureVector = pipeline.fit_transform(listOfTriples)

#featureVector.toarray()



#class NormalisedDocsList(BaseEstimator, TransformerMixin):
#    """Extract normalized string from each document, put into list of docs
#     to pass to desired text vectorizer e.g. CountVectorizer or TfidfVectorizer"""
#    def fit(self, x, y=None):
#        return self
#    def transform(self, listOftriples):
#        docsList = []
#        for tripleSetCurrentDoc in listOftriples:
#            tokenList = []
#            for triple in tripleSetCurrentDoc:
#                token = triple[0]
#                #normalising steps some adapted from RTRGO paper
#                token = token.lower()
#                token = token.replace("#","")
#                tokenList.append(token)
#            docsList.append(' '.join(tokenList))
#        return docsList
#            

#n = NormalisedDocsList()
#n.transform(listOfTriples)




#countvecpipe = Pipeline([
#        #('selector', ItemSelector(key='body')),
#        ('normed-docs', NormalisedDocsList()),  # returns a list of normalised docs e.g. text from doc
#        ('count-vect', CountVectorizer()),  # vectorized n-gram counts
#    ])

#        
#countVector = countvecpipe.fit_transform(listOfTriples)

#countVector.toarray()

##merge features
#featpipe = FeatureUnion([('n-gram-vec',countvecpipe),('feat-vec',pipeline)])








#def mergeCSRwithNumpyArrays(csr_array,numpy_array):
#    '''
#    Inputs 1- csr_matrix (usually a sparse n-gram matrix)
#          2- numpy_array(usually non n-gram features)
#    Outputs a sparse csr_matrix to be passed into classifiers
#    NOTE: must be matching dimensions and must have same dimension
#    on concatenating axis'''
#    #TODO: If time, throw in error handling
#    concatedArray = numpy.concatenate((csr_array.toarray(),numpy_array), axis = 1)
#    return csr_matrix(concatedArray)


#class Vectorize(object):
#    def __init__(self,ngram_range=(1, 1),vocabulary=None,norm='l2'):
#        self.countVec =  CountVectorizer(analyzer=string.split, min_df=1,\
#                            ngram_range = ngram_range,vocabulary=vocabulary)
#        self.tfidfVec =  TfidfVectorizer(analyzer=string.split, min_df=1,\
#                            ngram_range = ngram_range,vocabulary=vocabulary,norm=norm)
##countVec =  CountVectorizer(analyzer=string.split, min_df=1,ngram_range=(1, 1),vocabulary=None)        
#        self.ngramArray = None
#        self.vocabulary = None
#     
#    def countTransform(self,corpus):
#        self.ngramArray = self.countVec.fit_transform(corpus)
#        self.vocabulary = self.countVec.vocabulary_
#    
#    def tfidfTransform(self,corpus):
#        self.ngramArray = self.countVec.fit_transform(corpus)
#        self.vocabulary = self.countVec.vocabulary_
