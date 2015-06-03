import numpy
from scipy.sparse import csr_matrix

import string #necessary for analyzer option for feature extractors to split unicode and strings
import sklearn
from sklearn.feature_extraction.text import (CountVectorizer,TfidfTransformer,TfidfVectorizer)



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
