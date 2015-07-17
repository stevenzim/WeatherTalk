from wxtalk import helper

import string #necessary for analyzer option for feature extractors to split unicode and strings
import time
from functools import partial  #used for lexical transformer
from itertools import islice #used for lexical transformer

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import (Pipeline,FeatureUnion)
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import (CountVectorizer, TfidfTransformer, TfidfVectorizer)

#some useful f's for transformers
first = lambda x: (x[0])
second = lambda x: (x[1])
last = lambda x: (x[-1])
lower = lambda x:  x.lower()

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
        return self

    def transform(self, listOfTriples,keysToDrop=[]):
        if keysToDrop != []:
            self.keysToDrop = keysToDrop
            
        listOfStats = [{'questmark_present': self.boolTest(tripleSetCurrentDoc,0,'?'),\
                    'urloremail_present': self.boolTest(tripleSetCurrentDoc,1,'U'),\
                    "hashtag_present":self.boolTest(tripleSetCurrentDoc,1,'#')}\
                     for tripleSetCurrentDoc in listOfTriples]
        listToReturn = helper.dropKeysVals(listOfStats, self.keysToDrop)
        return listToReturn


class NRCLexiconsExtractor(BaseEstimator, TransformerMixin):
    """Extract lexical features from each document which can then be passed to DictVectorizer
    This transformer is an adaptation of papers/lexicons discussed in section 3 of
    http://www.saifmohammad.com/WebPages/lexicons.html
    Pass in a list of tweets/document triples extracted from twitter NLP and return features proposed in paper.
    Options include lexicon = NRCHash or NRC140, gramTypes = unigrams/bigrams/pairs, tagType = token,hashtag,caps"""
    def __init__(self,lexicon,gramType = 'unigram',tagType = 'token'):
        self.lexicon = lexicon
        self.gramType = gramType
        self.tagType = tagType


        ###manual lexicon file details
        #Bing Liu lexicon path and files
        self.BingLiuPath = helper.getProjectPath() +  '/wxtalk/resources/lexicons/BingLiu/'       
        self.BingLiufile = {'unigram': self.BingLiuPath + 'BingLiu.json'}
        #MPQA lexicon path and files
        self.MPQAPath = helper.getProjectPath() +  '/wxtalk/resources/lexicons/MPQA/'       
        self.MPQAfile = {'unigram': self.MPQAPath + 'MPQA.json'}
        #NRCemotion lexicon path and files
        self.NRCemotionPath = helper.getProjectPath() +  '/wxtalk/resources/lexicons/NRC-emotion/'       
        self.NRCemotionfile = {'unigram': self.NRCemotionPath + 'NRC-emotion.json'}

        ###automatic lexicon file details
        #NRC 140 lexicon path and files
        self.NRC140Path = helper.getProjectPath() +  '/wxtalk/resources/lexicons/NRC-Sent140/'       
        self.NRC140files = {'unigram': self.NRC140Path + 'unigrams140.json',\
                            'bigram': self.NRC140Path + 'bigrams140.json',\
                            'pairs': self.NRC140Path + 'pairs140.json'}
        #NRC Hashtag lexicon path and files
        self.NRCHashPath = helper.getProjectPath() +  '/wxtalk/resources/lexicons/NRC-Hash/'       
        self.NRCHashfiles = {'unigram': self.NRCHashPath + 'unigramsHash.json',\
                            'bigram': self.NRCHashPath + 'bigramsHash.json',\
                            'pairs': self.NRCHashPath + 'pairsHash.json'} 

    def setLexicon(self,lexicon):
        '''Load desired lexicon based on input values'''
        if lexicon == 'BingLiu':
            self.lexicon = helper.loadJSONfromFile(self.BingLiufile[self.gramType])
        elif lexicon == 'MPQA':
            self.lexicon = helper.loadJSONfromFile(self.MPQAfile[self.gramType]) 
        elif lexicon == 'NRCemotion':
            self.lexicon = helper.loadJSONfromFile(self.NRCemotionfile[self.gramType]) 
        elif lexicon == 'NRC140':
            self.lexicon = helper.loadJSONfromFile(self.NRC140files[self.gramType])
        elif lexicon == 'NRCHash':
            self.lexicon = helper.loadJSONfromFile(self.NRCHashfiles[self.gramType]) 
        elif type(lexicon) == type({}):
            #this case put here to handle situation when dict is already loaded (e.g. when loading a pickle file)
            self.lexicon = lexicon
        else:
            raise TypeError("You need to provide a correct lexicon and or gramType")      


    def window(self,seq, n=2):
        #adapted from:https://docs.python.org/release/2.3.5/lib/itertools-example.html
        "Returns a sliding window (of width n) over data from the iterable"
        "   s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...                   "
        it = iter(seq)
        result = tuple(islice(it, n))
        if len(result) == n:
            yield result    
        for elem in it:
            result = result[1:] + (elem,)
            yield result
 
    def getListOfTags(self,listOfTriples):
        '''Provided list of document/tweet triples, return list of tags based on the gramType and tagType
        unigram will only extract single tokens, bigrams extracts window of tokens'''
        #TODO: gramType = pairs --> See details of this in "Sentiment Analysis of Short Informal Texts"
               # with unigrams and bigrams only, we get approx +.05 F-score, so perhaps this extra step will not provide a big gain, looking for quick wins
        #TODO: tagType = Caps, Hashtags
               #I have not found anything specific to show how this is done, nor any specifics to show it will work
               #hence these features are low priority PERHAPS remove option all together
        listOfTagsAllTriples = []
        for tripleSetCurrentDoc in listOfTriples:
            lowerTokens = map(lower,map(first, tripleSetCurrentDoc))
            if self.gramType == 'unigram':
                listOfTagsAllTriples.append(lowerTokens)
            if self.gramType == 'bigram':
                listOfBigrams = []
                for terms in self.window(lowerTokens,n=2):
                    listOfBigrams.append(' '.join(terms))
                listOfTagsAllTriples.append(listOfBigrams)
        return listOfTagsAllTriples
                
                   
    def getListOfScores(self,listOfTagsAllDocs):
        '''Provided list of document/tweet tags (e.g. unigrams extracted from set of document triples), 
        return list of lexicon scores based on occurance in lexicon'''
        listOfScoresAllDocs = []
        keyNames = set(self.lexicon.keys()) 
        for tagsCurrentDoc in listOfTagsAllDocs:
            currentDocScores = []
            for tag in tagsCurrentDoc:
                if tag in keyNames:
                    currentDocScores.append(self.lexicon[tag])
            if currentDocScores ==[]:
                #we need to put 0.0 for neutral score for none found and to prevent errors in further processing
                listOfScoresAllDocs.append([0.0])
            else:
                listOfScoresAllDocs.append(currentDocScores)
        #convert everything to float
        return map(partial(map,float),listOfScoresAllDocs)
    
    def getPositives(self,score):
        '''Provided scores, return only score if positive'''
        if score > 0.0:
            return score
            
    def getLastPositiveScore(self,listOfPosScores):
        '''If no positive scores return 0.0 else, return score of last pos score'''
        if listOfPosScores == []:
            return 0.0
        else:
            return listOfPosScores[-1]
                        
        
    def fit(self, x,y=None):
        return self

    def transform(self, listOfTriples):
        '''Transform list of Triples containing document/tweet triples to desired vector format for specificied
        NRC lexicon and options'''
        self.setLexicon(self.lexicon)

        #start_time = time.time()
        listOfTagsAllDocs = self.getListOfTags(listOfTriples)
        #print("ListOfTags Total elapsed time--- %s seconds ---" % (time.time() - start_time))
        listOfScoresAllDocs = self.getListOfScores(listOfTagsAllDocs)
        #print("ListOfScores Total elapsed time--- %s seconds ---" % (time.time() - start_time))
                       
        listOfFeatures = [{'total_count_posi': len(filter(self.getPositives,scores)),\
                    'total_score': round(sum(scores),3),\
                    'max_score': round(max(scores),3),\
                    'score_last_posi_token':round(self.getLastPositiveScore(filter(self.getPositives,scores)),3)}\
                     for scores in listOfScoresAllDocs]
        #print("ListofFeats Total elapsed time--- %s seconds ---" % (time.time() - start_time))
        return listOfFeatures

class POScountExtractor(BaseEstimator, TransformerMixin):
    '''Adaptation of POS count features used in both NRC 2013/2014 Semeval submissions'''

    def fit(self, x,y=None):
        return self

    def transform(self, listOfTriples):
        '''Transform list of Triples containing document/tweet triples to desired dictionary format of POS counts'''              
        listOfPOSdicts = []
        for tripleSetCurrentDoc in listOfTriples:
            #reset local POS dict
            localPOSdict = {'!': 0, '#': 0, '$': 0, '&': 0, ',': 0, 'A': 0,\
                '@': 0, 'E': 0, 'D': 0, 'G': 0, 'M': 0, 'L': 0, \
                'O': 0, 'N': 0, 'P': 0, 'S': 0, 'R': 0, 'U': 0,\
                 'T': 0, 'V': 0, 'Y': 0, 'X': 0, 'Z': 0, '^': 0, '~': 0}
            docPOStags = map(second, tripleSetCurrentDoc)
            for tag in docPOStags:
                localPOSdict[tag] += 1
            listOfPOSdicts.append(localPOSdict)
        return listOfPOSdicts
        

###---------------encoding transformers-------------###
class capsCountExtractor(BaseEstimator, TransformerMixin):
    '''Adaptation of Capital count features used in both NRC 2013/2014 Semeval submissions
    Should count the total number of all caps words including hashtags for each tweet'''

    def fit(self, x,y=None):
        return self

    def transform(self, listOfTriples):
        '''Transform list of Triples containing document/tweet triples to desired dictionary format of capitilized token counts'''      
     
        capsCountDicts = []
        for tripleSetCurrentDoc in listOfTriples:   
            capsCountDicts.append({'total_count_caps':len(filter(lambda x: x.isupper(), map(first, tripleSetCurrentDoc)))} )
        return capsCountDicts


class hashCountExtractor(BaseEstimator, TransformerMixin):
    '''Adaptation of hashtag counts used in both NRC 2013/2014 Semeval submissions
    Should count the total number of hashtags for each tweet'''

    def fit(self, x,y=None):
        return self

    def transform(self, listOfTriples):
        '''Transform list of Triples containing document/tweet triples to desired dictionary format of hashtag counts'''              
        hashtagCountDicts = []
        for tripleSetCurrentDoc in listOfTriples:
            hashtagCountDicts.append({'total_count_hash':len(filter(lambda x: x=='#', map(second, tripleSetCurrentDoc)))})
        return hashtagCountDicts

class elongWordCountExtractor(BaseEstimator, TransformerMixin):
    '''Adaptation of elongated word counts used in both NRC 2013/2014 Semeval submissions
    Should count the total number of words with more than 2 consecutive same characters (e.g. wooorld matchs, woorld does not) for each tweet'''

    def fit(self, x,y=None):
        return self

    def transform(self, listOfTriples):
        '''Transform list of Triples containing document/tweet triples to desired dictionary format of elongated counts'''              
        hashtagCountDicts = []
        for tripleSetCurrentDoc in listOfTriples:
            hashtagCountDicts.append({'total_count_hash':len(filter(lambda x: x=='#', map(second, tripleSetCurrentDoc)))})
        return hashtagCountDicts
        
        
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

