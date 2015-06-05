#TODO: Perhaps get rid of this module, likely don't need code below
import numpy
from scipy.sparse import csr_matrix

import string #necessary for analyzer option for feature extractors to split unicode and strings
import sklearn
from sklearn.feature_extraction.text import (CountVectorizer,TfidfTransformer,TfidfVectorizer)

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
