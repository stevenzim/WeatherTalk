from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import (Pipeline,FeatureUnion)
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import (CountVectorizer, TfidfTransformer, TfidfVectorizer)
import string #necessary for analyzer option for feature extractors to split unicode and strings
import helper

class TriplesYsExtractor(BaseEstimator, TransformerMixin):
    '''Provided a list of dictionaries containing triples created by Twitter NLP
    --> return a list of TweetNLP triples representing each tweet
    if option ysKeyname is provided, then list containing expected results is also returned
    triplesList and ysList can be passed to pipeline
    options - ykey = keyname containing expected results, necessary for training'''
    def fit(self, x, y=None):
        return self
    def transform(self, listOfDicts ,\
        triplesKeyName = "tagged_tweet_triples", ysKeyName=None):
        #TODO: Consider throwing error message if y's key name doesn't exist in dictionary
        #TODO: Rather than hard coding default keynames, perhaps change it to required args
        #       with an error thrown if keyname does not exist
        triplesList = [] #list of triples
        ysList = [] #list of expected ys
        for dict in listOfDicts:
            triplesList.append(dict[triplesKeyName])
            if ysKeyName != None:
                ysList.append(dict[ysKeyName])
        if ysKeyName != None:
            return triplesList, ysList  #we want to grab expected results
        else:
            return triplesList    #no expected results, therefore don't return ys

 
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
    #TODO: Dealwith/Debug situation when no additional features will be added
    #      fit transform does not like it when all features are removed.
    #      WORKAROUND IS TO REMOVE THIS STEP FROM PIPELINE
    def __init__(self,keysToDrop=[]):
        #added this to allow for grid search to work.  Per discussuion:
        # http://stackoverflow.com/questions/23174964/how-to-gridsearch-over-transform-arguments-within-a-pipeline-in-scikit-learn
        # BaseEstimator requires __init__ in order for GridSearchCV to iterate over passed in params
        self.keysToDrop = keysToDrop
    
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
            

    def fit(self, x,y=None):
        #print "fit"
        #print self.keysToDrop
#        if keysToDrop != []:
#            self.keysToDrop = keysToDrop
        return self

    def transform(self, listOfTriples,keysToDrop=[]):
        #print "transform"
        #print self.keysToDrop
        if keysToDrop != []:
            self.keysToDrop = keysToDrop
            
        listOfStats = [{'questmark_present': self.boolTest(tripleSetCurrentDoc,0,'?'),\
                    'urloremail_present': self.boolTest(tripleSetCurrentDoc,1,'U'),\
                    "hashtag_present":self.boolTest(tripleSetCurrentDoc,1,'#')}\
                     for tripleSetCurrentDoc in listOfTriples]
#        print "Hello 1"
#        print self.keysToDrop
#        print "Hello 2"
#        print keysToDrop
        listToReturn = helper.dropKeysVals(listOfStats, self.keysToDrop)
        return listToReturn


class CustomCountVectorizer(BaseEstimator, TransformerMixin):
    '''
    Custom count vectorizer IDEALLY allows for vocabulary to be accessed after pipeline.transform is runs
    Still struggling with how to do this.
    '''
    #TODO: REMOVE THIS WHEN PROTOTYPE COMPLETE
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

