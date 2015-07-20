from wxtalk import helper

import string #necessary for analyzer option for feature extractors to split unicode and strings
import time
import re
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
greaterZeroBool = lambda x: True if (x>0.0) else False
lessZeroBool = lambda x: True if (x<0.0) else False
greaterZeroVal = lambda x: x if (x>0.0) else 0.0
lessZeroVal = lambda x: x if (x<0.0) else 0.0
true = lambda x: True if (x==True) else False
removeNegateStr = lambda token: token.replace('_NEG','')  #removes any negation string that may have been added in TriplesYsExtractor


class TriplesYsExtractor(BaseEstimator, TransformerMixin):
    '''Provided a list of dictionaries containing triples created by Twitter NLP
    --> return a list of TweetNLP triples representing each tweet
    if option ysKeyname is provided, then list containing expected results is also returned
    triplesList and ysList can be passed to pipeline
    options - ykey = keyname containing expected results, necessary for training'''
    def __init__(self,negateTweet = False):
        self.negateTokenBool = False    #boolean value to determine whether current token should be negated if True then _NEG is attached to token
        self.negateTweet = negateTweet #user specified, if True, then tokens for tweets will have negation run on them, otherwise false.

    def setNegate(self,tripleIn):
        '''Per multiple research papers, indications are that _NEG should be added to negated components of a tweet
        Takes an NLP tripleset from tweet tagger and returns tripleset with _NEG added appropriately'''
        #TODO: additional test for negation
        #NOTE: hash symbols are not removed from front of corpus, which will add minor noise
        token = tripleIn[0]
        posTag = tripleIn[1]
        score = tripleIn[2]
        tripleOut = []
        
        #RE from christopherpotts
        negateRe = re.match(r'(?:never|no|nothing|nowhere|noone|none|not|\
        havent|hasnt|hadnt|cant|couldnt|shouldnt|wont|\
        wouldnt|dont|doesnt|didnt|isnt|arent|aint)$|.*nt$|.*n\'t$',lower(token))
        if negateRe:
            self.negateTokenBool = True
        if self.negateTokenBool:  
            endNegateRe = re.match(r'[.:;!?]$',token)
            if endNegateRe:
                self.negateTokenBool = False
                return [token,posTag,score]
            else:
                token = token + '_NEG'
                return [token,posTag,score]
        else:
            return [token,posTag,score]

    def fit(self, x, y=None):
        return self

    def transform(self, listOfDicts ,\
        triplesKeyName = "tagged_tweet_triples", ysKeyName=None):
        #TODO: Rather than hard coding default keynames, perhaps change it to required args
        #       with an error thrown if keyname does not exist
        #global negativeBool
        triplesList = [] #list of triples
        ysList = [] #list of expected ys
        
        if self.negateTweet:
            #run negation if self.negateTweet = True
            for dict in listOfDicts:
                negatedTriples = map(lambda triple: self.setNegate(triple),dict[triplesKeyName])
                triplesList.append(negatedTriples)
                if ysKeyName != None:
                    ysList.append(dict[ysKeyName])
                self.negateTokenBool = False #reset negateTokenBool at the end of each tweet
        else:
            #don't run negation and just keep original tokens
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
    Fully extract and normalize the text to string format necessary for Doc or Idf vectorizers
    Per preprocessing from NRC, RTRGO, GU-MLT-LT
    This is in preparation of n-gram extraction
    You can pass in various normalizaion options
    The output normalisedDocsList can then be passed to count or tfidf vectorizer'''
    def __init__(self,lowercase=True,hashNormalise=True,digitNormalise=False,urlNormalise = True,userNameNormalise=True):
        self.lowercase = lowercase
        self.hashNormalise = hashNormalise
        self.digitNormalise = digitNormalise
        self.urlNormalise = urlNormalise
        self.userNameNormalise = userNameNormalise
    def fit(self, x, y=None):
        return self
    def transform(self, listOfDocumentsWithTriples):
        normalisedDocsList = []  #list of docs to output
        for currentDocTriples in listOfDocumentsWithTriples:
            tokenList = []
            negationCount = 0
            negativeBool = False
            for triple in currentDocTriples:
                #normalise each token per RTRGO paper
                #TODO: Could create different normalisation functions/options to try
                #TODO: Create a test to verify this works
                token = triple[0]
                if self.lowercase:
                    token = token.lower()
                if self.hashNormalise:
                    token = token.replace("#","")
                if self.digitNormalise:
                    token =  re.sub(r'\d', '0', token)  #replace all digits with 0 per GU-MLT-LT
                if self.urlNormalise:
                    if triple[1] == 'U' :
                        token = 'URL'
                if self.userNameNormalise:
                    if triple[1] == '@' :
                        token = 'USER'  
                tokenList.append(token)
            normalisedDocsList.append(' '.join(tokenList))
        return normalisedDocsList


class ClusterExtractor(BaseEstimator, TransformerMixin):
    '''Provided a list of documents containing TweetNLP triples that may have been negated.  
    Extract a list of CMU cluster IDs
    As no python wrapper for the CMU tagger was found, this is a custom solution
    For more about the CMU cluster tagger see: http://www.ark.cs.cmu.edu/TweetNLP/
    The output CMUclusterIDlist can then be passed to count or tfidf vectorizer
        lexicon was created from cmu cluster file.  3 steps give overview of how it was done.  Vocabulary file must be loaded into count/tfidf vectorizer for accurate counts
        see convertCMUorig.py in resources/scripts/CMUclusterScript/
        1- built a vocabulary to load into CountVectorizer should be 1000 cluster vals  Key = binary value Val = feature number
        2- created a lexicon/dictionary with key = token and val equal to binary value
        3- For each tweet build a string of binary cluster vals that can be split on string.split.   If token not in lexicon, add nothing to list
    '''
    def fit(self, x, y=None):
        return self
    def transform(self, listOfDocumentsWithTriples):
        clusterLexicon =  helper.loadLexicon('cmu-cluster-lex')
        clusterWords = set(clusterLexicon.keys())
        CMUclusterIDlist = []  #list of id strings concatenated together and to return, each item in list is one tweet
        for currentDocTriples in listOfDocumentsWithTriples:
            tokenList = []
            for triple in currentDocTriples:
                #normalise each token to match CMU expected format
                token = triple[0]
                token = removeNegateStr(token)
                token = token.lower()
                
                #get cluster id and update token
                if token in clusterWords:
                    tokenList.append(clusterLexicon[token])
                                
            CMUclusterIDlist.append(' '.join(tokenList))
        return CMUclusterIDlist




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

    def window(self,seq, n=2):
        #Taken from example found here: from:https://docs.python.org/release/2.3.5/lib/itertools-example.html
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
            lowerTokens = map(lambda token: token.replace('_neg',''),lowerTokens)  #remove negation tags
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
  
                      
        
    def fit(self, x,y=None):
        return self

    def transform(self, listOfTriples):
        '''Transform list of Triples containing document/tweet triples to desired vector format for specificied
        NRC lexicon and options'''
        
        lastSentiScore = lambda x: last(x) if (len(x) >0) else 0.0
        self.lexicon =  helper.loadLexicon(self.lexicon,self.gramType)

        listOfTagsAllDocs = self.getListOfTags(listOfTriples)
        listOfScoresAllDocs = self.getListOfScores(listOfTagsAllDocs)
                       
        listOfFeatures = [{#pos scores
                            'total_count_pos': len(filter(true,map(greaterZeroBool,scores))),\
                            'total_score_pos': round(sum(filter(greaterZeroVal,scores)),3),\
                            'max_score_pos': round(max(map(greaterZeroVal,scores)),3),\
                            'score_last_pos':round(lastSentiScore(filter(greaterZeroVal,scores)),3),\
                            #neg scores
                            'total_count_neg': len(filter(true,map(lessZeroBool,scores))),\
                            'total_score_neg': round(sum(filter(lessZeroVal,scores)),3),\
                            'min_score_neg': round(min(map(lessZeroVal,scores)),3),\
                            'score_last_neg':round(lastSentiScore(filter(lessZeroVal,scores)),3)}\
                            for scores in listOfScoresAllDocs]
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
        

###---------------negation transformer -------------###


class negatedSegmentCountExtractor(BaseEstimator, TransformerMixin):
    '''Adaptation of negation count feature extraction used in both NRC 2013/2014 Semeval submissions
    Originally from Pang et al., 2002.  Regular expression from Christopher potts http://sentiment.christopherpotts.net/lingstruc.html.
    Also helpful was Webis: An Ensemble for Twitter Sentiment Detection (Hagen, MatthiasPotthast, MartinBuchner, Michel Stein, Benno
    
    FOR ACCURATE COUNT REQUIRES  TRIPLES YS TRANSFORMER TO BE RUN WITH negateTweet = True'''
    #TODO: Future work would further investigate with authors if the _NEG tag added to token was implemented with lexicons.  Based on research, there is no evidence this was implemented,
    #however wording in literature may indicate otherwise
    #NOTE: If you do want to include these in unigrams, perhaps consider adding the _NEG as a preprocessing step after NLP triple tagger
    def fit(self, x,y=None):
        return self
        
    def countNegatedContexts(self,tripleSetCurrentDoc):
        '''Function to get the count of negation contexts in tweets, where a negation context is each time 
        a tweet switches not negative context to a negative context,an adaptation of code from 
       Webis: An Ensemble for Twitter Sentiment Detection (Hagen, MatthiasPotthast, MartinBuchner, Michel Stein, Benno'''
        negatedTokenBools = map(lambda token: '_NEG' in token ,map(first, tripleSetCurrentDoc))
        negatedSegment = False
        negationCount = 0
        for curBool in negatedTokenBools:
            if curBool:
                negatedSegment = True
            if negatedSegment:
                if curBool == False:
                    negationCount +=1
                    negatedSegment = False
        if negatedSegment:
            #handle situation when no punctuation or end of tweet occurs
            negationCount +=1

        return negationCount

    def transform(self, listOfTriples):
        '''Transform list of Triples containing document/tweet triples to desired dictionary format of negated context counts'''              
        negatedContextCountDicts = []
        for tripleSetCurrentDoc in listOfTriples:
            negatedContextCountDicts.append(
            {'negation_count':self.countNegatedContexts(tripleSetCurrentDoc)
            })
        return negatedContextCountDicts
      

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
        elongCountDicts = []
        regex = re.compile(r'(\w)\1{2,}')  #regex to match 3 or more repeating chars e.g. 'helllo' but not 'hello'
        for tripleSetCurrentDoc in listOfTriples:
            elongCountDicts.append({'total_count_elong':len(filter(lambda token: token if ((regex.search(token)) !=None) else None,map(first, tripleSetCurrentDoc)))})
        return elongCountDicts
        

class punctuationFeatureExtractor(BaseEstimator, TransformerMixin):
    '''Adaptation of punctuation feature extraction used in both NRC 2013/2014 Semeval submissions
    Should return counts where !!,!?,?? or more consecutive ! & ? occur and True if last token contains ! and True if last token contains ?'''

    def fit(self, x,y=None):
        return self

    def transform(self, listOfTriples):
        '''Transform list of Triples containing document/tweet triples to desired dictionary format of elongated counts'''              
        punctuationCountDicts = []
        reExclaim = re.compile(r'!{2,}')  #regex to match consecutive exclamation marks
        reQuest = re.compile(r'\?{2,}')  #regex to match consecutive question marks
        reBoth = re.compile(r'(!\?|\?!){1,}')  #regex to match consecutive question marks
        for tripleSetCurrentDoc in listOfTriples:
            punctuationCountDicts.append(
            {'count_contig_seq_exclaim':len(filter(lambda token: token if ((reExclaim.search(token)) !=None) else None,map(first, tripleSetCurrentDoc))),
            'count_contig_seq_question':len(filter(lambda token: token if ((reQuest.search(token)) !=None) else None,map(first, tripleSetCurrentDoc))),
            'count_contig_seq_both':len(filter(lambda token: token if ((reBoth.search(token)) !=None) else None,map(first, tripleSetCurrentDoc))),
            'last_toke_contain_quest':'?' in first(last(tripleSetCurrentDoc)),
            'last_toke_contain_exclaim':'!' in first(last(tripleSetCurrentDoc))
            })
        return punctuationCountDicts



class NRCemoticonExtractor(BaseEstimator, TransformerMixin):
    """Extract emoticon features from each document which can then be passed to DictVectorizer
    This transformer is an adaptation of papers/lexicons discussed in section 3 of
    http://www.saifmohammad.com/WebPages/lexicons.html
    Pass in a list of tweets/document triples extracted from twitter NLP and return emoticon features proposed in paper.
    NOTE: The KLUE emoticon dictionary has been used for these features as NRC authors did not provide a clear enough dictionary for 
    identifying pos/neg emoticons"""
    def __init__(self,lexicon):
        self.lexicon = lexicon

    def fit(self, x,y=None):
        return self

    def transform(self, listOfTriples):
        '''Transform list of Triples containing document/tweet triples to desired vector format for specificied
        NRC lexicon and options'''
        
        self.lexicon = helper.loadLexicon(self.lexicon)
        keyNames = set(self.lexicon.keys()) 
        
 
        emoticonFeatureDicts = []
        for tripleSetCurrentDoc in listOfTriples:
            tokens = map(first,tripleSetCurrentDoc)
            tokens = map(removeNegateStr,tokens)
            emoticonScores = map(lambda token: self.lexicon[token] if (token in keyNames)  else 0.0 ,tokens)
            posBools = map(greaterZeroBool,emoticonScores)
            negBools = map(lessZeroBool,emoticonScores)  
            emoticonFeatureDicts.append({'positive_emoticon_present': any(posBools),\
                                'negative_emoticon_present': any(negBools),\
                                'last_emoticon_pos': last(posBools),\
                                'last_emoticon_neg':last(negBools)})
        return emoticonFeatureDicts

#------KLUE FEATURES -----
#----token count----
class TokenCountExtractor(BaseEstimator, TransformerMixin):
    '''KLUE paper used token counts as feature, hence here it is implement.  Simply take the length of tweet triple.'''

    def fit(self, x,y=None):
        return self

    def transform(self, listOfTriples):
        '''Transform list of Triples to a list of counts of token'''      
        tokenCountDicts = []
        for tripleSetCurrentDoc in listOfTriples:   
            tokenCountDicts.append({'token_count':len(tripleSetCurrentDoc)} )
        return tokenCountDicts

class KLUEpolarityExtractor(BaseEstimator, TransformerMixin):
    """Extract emoticon features from each document which can then be passed to DictVectorizer
    This transformer is an adaptation of of the KLUE Semeval 2013 submission
    Pass in a list of tweets/document triples extracted from twitter NLP and desired polarity features for
    AFINN lexicon.
    """
    def __init__(self,lexicon='klue-afinn'):
        self.lexicon = lexicon

    def fit(self, x,y=None):
        return self

    def transform(self, listOfTriples):
        '''Transform list of Triples containing document/tweet triples to desired vector format for specificied
        KLUE polarity dictionary converter'''
        
        self.lexicon = helper.loadLexicon(self.lexicon)
        keyNames = set(self.lexicon.keys()) 
        emoticonFeatureDicts = []
        for tripleSetCurrentDoc in listOfTriples:
            tokens = map(first,tripleSetCurrentDoc)
            tokens = map(removeNegateStr,tokens)
            tokens = map(lower,tokens)
            #scores = map(lambda token: self.lexicon[token],tokens)
            emoticonScores = map(lambda token: self.lexicon[token] if (token in keyNames)  else 0.0 ,tokens)
            posBools = map(greaterZeroBool,emoticonScores)
            negBools = map(lessZeroBool,emoticonScores)  
            numPos = len(filter(true,posBools))
            numNeg = len(filter(true,negBools))
            numPolarTokens = numPos + numNeg
            if numPolarTokens == 0.0: #avoid division by zero
                numPolarTokens = 1.0
            totalScore = sum(emoticonScores)
            meanScore = totalScore/(numPolarTokens)
            emoticonFeatureDicts.append({'total_count_pos': numPos,\
                                'total_count_neg': numNeg,\
                                'total_count_polar': numPos + numNeg,\
                                'mean_polarity':meanScore})
        return emoticonFeatureDicts        
        
#--------prototype stuff-------------        
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

