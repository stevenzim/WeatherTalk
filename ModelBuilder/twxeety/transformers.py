import numpy as np
import string #necessary for analyzer option for feature extractors to split unicode and strings
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import (Pipeline,FeatureUnion)
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import (CountVectorizer, TfidfTransformer, TfidfVectorizer)
#from sklearn.svm import SVC
import helper

#TODO: BIG ITEMS -
#1) Change Docs Triples Ys Extractor, to simply a triples and Ys extractors
#2) Create test for docs extract
#3) Grid Search with options dictionary


class DocsTriplesYsExtractor(BaseEstimator, TransformerMixin):
    '''Provided a list of dictionaries containing triples created by Twitter NLP
    & normalised strings --> return a document list of string and triples list 
    document list can be passed to tfidfVectorizer for example
    and triples list can be passed to other transformer
    options - ykey = keyname containing expected results, necessary for training'''
    def fit(self, x, y=None):
        return self
    def transform(self, listOfDicts ,\
        docsKeyName ="normal_string_rtrgo" , triplesKeyName = "tagged_tweet_triples", ysKeyName=None):
        #TODO: Consider throwing error message if y's key name doesn't exist in dictionary
        #TODO: Rather than hard coding default keynames, perhaps change it to required args
        #       with an error thrown if keyname does not exist
        docsList = []  #list of docs
        triplesList = [] #list of triples
        ysList = [] #list of expected ys
        for dict in listOfDicts:
            docsList.append(dict[docsKeyName])
            triplesList.append(dict[triplesKeyName])
            if ysKeyName != None:
                ysList.append(dict[ysKeyName])
        if ysKeyName != None:
            return docsList, triplesList, ysList  #we want to grab expected results
        else:
            return docsList, triplesList    #no expected results, therefore don't return ys



#EXAMPLE PIPELINE
#from sklearn.linear_model import SGDClassifier
#from sklearn.grid_search import GridSearchCV
#ngramCountPipe = Pipeline([\
#            ('docs',tran.DocsExtractor()),\
#            ('count',tran.CountVectorizer(analyzer=string.split))])

#ngramTfidfPipe = Pipeline([\
#            ('docs',tran.DocsExtractor()),\
#            ('tf-idf',tran.TfidfVectorizer(analyzer=string.split))])

#otherFeaturesPipe = Pipeline([\
#            ('text-feats-dict',tran.TextFeaturesExtractor()),\
#            ('text-feats-vec',tran.DictVectorizer())])

#features = FeatureUnion([
#            ('ngrams',ngramCountPipe),
#            ('others',otherFeaturesPipe)])

#pipeline = Pipeline([\
#            ('features',features),
#            ('clf',SGDClassifier())])

#inFile = 'tests/test-data/SemEval/3-SemEvalFeatures.json'
#data = helper.loadJSONfromFile(inFile)           
#ed = tran.DocsTriplesYsExtractor()
#docsList, triplesList, ysList = ed.transform(data,ysKeyName = 'sentiment_num')
   
class DocsExtractor(BaseEstimator, TransformerMixin):
    '''Provided a list of documents containing TweetNLP triples.  
    Fully extract and normalize the text to string format necessary for Doc or Idf vectorizers'''
    def fit(self, x, y=None):
        return self
    def transform(self, listOfDocumentsWithTriples):
        normalisedDocsList = []  #list of docs to output
        for currentDocTriples in listOfDocumentsWithTriples:
            tokenList = []
            for triple in currentDocTriples:
                #normalise each token per RTRGO paper
                #TODO: Could create different normalisation functions/options to try
                #TODO: Create a test to verify this works
                token = triple[0]
                token = token.lower()
                token = token.replace("#","")
                tokenList.append(token)
            normalisedDocsList.append(' '.join(tokenList))
        return normalisedDocsList


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
            

    def fit(self, x, y=None):
        return self

    def transform(self, listOfTriples, keysToDrop=[]):
        #TODO: Need to confirm that order is guaranteed when these results are passed to DictVectorizer
        listOfStats = [{'questmark_present': self.boolTest(tripleSetCurrentDoc,0,'?'),\
                    'urloremail_present': self.boolTest(tripleSetCurrentDoc,1,'U'),\
                    "hashtag_present":self.boolTest(tripleSetCurrentDoc,1,'#')}\
                     for tripleSetCurrentDoc in listOfTriples]
        listToReturn = helper.dropKeysVals(listOfStats, keysToDrop)
        return listToReturn


class CustomCountVectorizer(BaseEstimator, TransformerMixin):
    '''
    Custom count vectorizer IDEALLY allows for vocabulary to be accessed after pipeline.transform is runs
    Still struggling with how to do this.
    '''
    def __init__(self,ngram_range=(1, 1),vocabulary=None,norm='l2'):
        self.countVec =  CountVectorizer(analyzer=string.split, min_df=1,\
                            ngram_range = ngram_range,vocabulary=vocabulary)
        self.ngramArray = None
        self.vocabulary = None
    def fit(self, x, y=None):
        return self
    def transform(self, listOfDocs):
        self.ngramArray = self.countVec.fit_transform(listOfDocs)
        self.vocabulary = self.countVec.vocabulary_
        return self.ngramArray, self.vocabulary

#pipeline, vocabulary = Pipeline([('docs',tran.CustomCountVectorizer)])
                     
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
