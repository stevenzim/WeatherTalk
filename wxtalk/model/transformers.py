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

from nltk.stem.porter import PorterStemmer

import pprint


#some useful f's for transformers
first = lambda x: (x[0]) if (len(x) >0) else ''
second = lambda x: (x[1]) if (len(x) >1) else ''
last = lambda x: (x[-1]) if (len(x) >0) else ''
lower = lambda x:  x.lower()
upper = lambda x:  x.upper()
greaterZeroBool = lambda x: True if (x>0.0) else False
lessZeroBool = lambda x: True if (x<0.0) else False
greaterZeroVal = lambda x: x if (x>0.0) else 0.0
lessZeroVal = lambda x: x if (x<0.0) else 0.0
true = lambda x: True if (x==True) else False
removeNegateStr = lambda token: token.replace('_NEG','')  #removes any negation string that may have been added in TriplesYsExtractor
collapseToken = lambda token: re.sub(r'(.)\1+', r'\1\1', token) #collapse 3 or more characters down to 2


class TweetTransformer(BaseEstimator, TransformerMixin):
    '''
    Represents one Tweet and saves some features and the preprocessed versions of the Tweet
    adapted from Webis 2015 Semeval Java Code

    This object is created for each tweet that passes through pipeline.  
    This will be incorporated in the TriplesYsExtractor to initialize tweet representation for all 
    following pipelines and feature unions
    The optional params are
    1  - user normalisation string - optional None removes token and any string will replace any username 
            anything else is put in place. i.e. 'USER' will be put into token string (and thus included in unigram vocab)
    2  - url normalisation string - optional None removes token and 
            anything else is put in place. i.e. 'URL' will be put into token string (and thus included in unigram vocab)
    3  - hashNormalise will remove #symbol from tweets
    4  - digitNormalise will replace all digits with a 0
    Expected param for tweet transformation is
    1 - list of dicts containing original tweet text and extracted nlp triples
    Optional params
    1 - key name for triples list in dict if different from default
    2 - key name for expected classes e.g. Ys.  default is None
    '''
    def __init__(self,userNorm = None,urlNorm = None,hashNormalise=False,digitNormalise=False):
        '''init object'''
        #input params
        self.userNorm = userNorm  #None removes token
        self.urlNorm = urlNorm  #None removes
        self.hashNormalise = hashNormalise
        self.digitNormalise = digitNormalise
        
        #raw input vals
        self.rawTweet = None          #the raw tweet text
        self.cmuRawTextTriples = None #triples extracted from cmu tagger for raw text
        self.raw_token_list = None

        #normalised tweet vals
        self.normalised_token_list = None
        self.normalised_string = None

        #tweet stems
        self.stem_list = None
        self.stem_string = None

        #negated tweet vals
        self.negated_list = None
        self.negated_string = None
        self.negated_count = None

        #collapsed tokens of normalised tweet tokens
        self.collapsed_token_list = None
	    
    def setNormalisedTweet(self):
        '''sets normalised list and string value based on raw token list'''
        updatedTokenList = []  
        for triple in self.cmuRawTextTriples:
            token = triple[0]
            pos = triple[1]
            if (pos =='@') and (self.userNorm == None):
                continue
            if (pos =='U') and (self.urlNorm == None):
                continue            
            if (pos =='@'):
                token = self.userNorm
            if (pos =='U'):
                token = self.urlNorm    
            if self.hashNormalise:
                token = token.replace("#","")
            if self.digitNormalise:
                token =  re.sub(r'\d', '0', token)  #replace all digits with 0 per GU-MLT-LT
            token = token.lower()
            updatedTokenList.append(token)
        self.normalised_token_list = updatedTokenList
        self.normalised_string = ' '.join(updatedTokenList)
        #print self.normalised_token_list
        #print self.normalised_string
    
    def setTweetStems(self):
        '''sets stems list and string values based on normalised token list'''
        stemmer = PorterStemmer()
        self.stem_list = map(lambda token: stemmer.stem(token),self.normalised_token_list)
        self.stem_string = ' '.join(self.stem_list )
        #print self.stem_list
        #print self.stem_string
       
    def setTweetNegationVals(self):
        '''sets negation list, string  and count values based on normalised token list  
        Adaptation of negation count/feature extraction used in both NRC 2013/2014 Semeval submissions
        Originally from Pang et al., 2002.  Regular expression from Christopher potts http://sentiment.christopherpotts.net/lingstruc.html.
        Also helpful was Webis: An Ensemble for Twitter Sentiment Detection (Hagen, MatthiasPotthast, MartinBuchner, Michel Stein, Benno'''
        negatedTokenList = []
        negateTokenBool = False
        negateCount = 0   
        
        for token in self.normalised_token_list:
            #RE from christopherpotts
            negateRe = re.match(r'(?:never|no|nothing|nowhere|noone|none|not|\
            havent|hasnt|hadnt|cant|couldnt|shouldnt|wont|\
            wouldnt|dont|doesnt|didnt|isnt|arent|aint)$|.*nt$|.*n\'t$',token)
            if negateRe:
                negateTokenBool = True
            if negateTokenBool:  
                endNegateRe = re.match(r'[.:;!?]$',token)
                if endNegateRe:
                    negateTokenBool = False
                    negatedTokenList.append(token)
                    negateCount += 1
                else:
                    token = token + '_NEG'
                    negatedTokenList.append(token)
            else:
                negatedTokenList.append(token)    
                
        if (negateCount ==0) and (negateTokenBool ==True):
            negateCount = 1   

        self.negated_list = negatedTokenList
        self.negated_string = ' '.join(negatedTokenList)
        self.negated_count = negateCount
        
        #print self.negated_list
        #print self.negated_string
        #print self.negated_count
        
    def setCollapsedTweetVals(self):
        '''sets list of collapsed tokens based on normalised token list'''
        self.collapsed_token_list = map(collapseToken,self.normalised_token_list)
        #print self.collapsed_token_list
        

    def getPipelineTweetDict(self):
        '''Builds and returns the internal tweet representation for pipeline'''
        self.setNormalisedTweet()
        self.setTweetStems()
        self.setTweetNegationVals()
        self.setCollapsedTweetVals()
        
        pipelineTweet = {'nlp_triples' : self.cmuRawTextTriples,\
                        'raw_string' : self.rawTweet,\
                        'raw_token_list' : self.raw_token_list,\
                        'pos_token_list' : map(second,self.cmuRawTextTriples),\
                        'normalised_token_list' : self.normalised_token_list,\
                        'normalised_string' : self.normalised_string,\
                        'stem_list' : self.stem_list,\
                        'stem_string' : self.stem_string,\
                        'negated_token_list' : self.negated_list,\
                        'negated_string' : self.negated_string,\
                        'collapsed_token_list' : self.collapsed_token_list,\
                        'negation_count' : self.negated_count,\
                        'stanford_token_list' : None,\
                        'stanford_pos_list' : None}
        return pipelineTweet

    def fit(self, x, y=None):
        return self

    def transform(self, listOfTweetsWithTriples,\
        triplesKeyName = "tagged_tweet_triples", ysKeyName=None):
            '''Transforms a set of tweets tagged with nlp triples to desired format for pipeline'''
            transformedTweetList = []
            expectedYsList =[]
            for currentTweet in listOfTweetsWithTriples:
                self.rawTweet = currentTweet['text']
                self.cmuRawTextTriples = currentTweet[triplesKeyName]
                self.raw_token_list = map(first,self.cmuRawTextTriples)
                transformedTweetList.append(self.getPipelineTweetDict())
                if ysKeyName != None:
                    expectedYsList.append(currentTweet[ysKeyName])   
            
#            pp = pprint.PrettyPrinter(indent=4)
#            pp.pprint(transformedTweetList)
            #print triplesList             
            if ysKeyName != None:
                #these values returned for when you are training model
                return transformedTweetList, expectedYsList  #
            else:
                #values returned for unseen data with unknown classes
                return transformedTweetList                                

class DocsExtractor(BaseEstimator, TransformerMixin):
    '''Provided a list of transformer tweets.  
    return a list of desired values from transformed tweet based on input key name
    negated_string is default per Webis paper.  The transformed output can be passed to tf/idf or count vectorizer
    '''
    def __init__(self,transformedTweetKeyName = 'negated_string'):
        self.transformedTweetKeyName= transformedTweetKeyName #name of key containing list desired vals

    def fit(self, x, y=None):
        return self

    def transform(self, transformedTweets):
        #print "DocsExtractor"
        #print transformedTweets
        return map(lambda tweet: tweet[self.transformedTweetKeyName], transformedTweets)


class NRCLexiconsExtractor(BaseEstimator, TransformerMixin):
    """Extract lexical features from each document which can then be passed to DictVectorizer
    This transformer is an adaptation of papers/lexicons discussed in section 3 of
    http://www.saifmohammad.com/WebPages/lexicons.html
    Pass in a list of transformed tweets and keyname containining tweet tokens in desired format 
    and returns features proposed in paper.
    Options include lexicon = NRCHash or NRC140, gramTypes = unigrams/bigrams/pairs, tagType = token,hashtag,caps
    param tokenListKeyName is the key name in transformed tweet input that contains desired token format list """
    def __init__(self,lexicon,gramType = 'unigram',tagType = 'token',tokenListKeyName = 'negated_token_list'):
        self.lexicon = lexicon
        self.gramType = gramType
        self.tagType = tagType
        
        self.tokenListKeyName = tokenListKeyName

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
 
    def getListOfNgrams(self,transformedTweets):
        '''Provided list of transformed tweets, return list of ngrams based on the gramType and tagType
        unigram will only extract single tokens, bigrams extracts window of tokens'''
        #TODO: gramType = pairs --> See details of this in "Sentiment Analysis of Short Informal Texts"
               # with unigrams and bigrams only, we get approx +.05 F-score, so perhaps this extra step will not provide a big gain, looking for quick wins
        #TODO: tagType = Caps, Hashtags
               #Have not found anything specific to show how this is done, nor any specifics to show it will work
               #hence these features are low priority PERHAPS remove option all together
        ngramsAllTweets = []
        for tweet in transformedTweets:
            if self.gramType == 'unigram':
                ngramsAllTweets.append(tweet[self.tokenListKeyName])
            if self.gramType == 'bigram':
                listOfBigrams = []
                for terms in self.window(tweet[self.tokenListKeyName],n=2):
                    listOfBigrams.append(' '.join(terms))
                ngramsAllTweets.append(listOfBigrams)
        return ngramsAllTweets
                
                   
    def getListOfScores(self,listOfngramsAllTweets):
        '''Provided list of document/tweet ngrams (e.g. unigrams extracted from set of transformed tweets), 
        return list of lexicon scores based on occurance in lexicon'''
        listOfScoresAllTweets = []
        keyNames = set(self.lexicon.keys()) 
        for tagsCurrentTweet in listOfngramsAllTweets:
            currentTweetScores = []
            for tag in tagsCurrentTweet:
                if tag in keyNames:
                    currentTweetScores.append(self.lexicon[tag])
            if currentTweetScores ==[]:
                #put 0.0 for neutral score for none found... to prevent errors in further processing
                listOfScoresAllTweets.append([0.0])
            else:
                listOfScoresAllTweets.append(currentTweetScores)
        
        #convert everything to float
        return map(partial(map,float),listOfScoresAllTweets)
  
                      
        
    def fit(self, x,y=None):
        return self

    def transform(self, transformedTweets):
        '''Transform list of Tweets in internal format containing desired token format to retrieve desired
        NRC lexicon and options'''
        #print "NRC Lexicon Extract"
        #print transformedTweets
        lastSentiScore = lambda x: last(x) if (len(x) >0) else 0.0
        self.lexicon =  helper.loadLexicon(self.lexicon,self.gramType)

        ngramsAllTweets = self.getListOfNgrams(transformedTweets)  #a list of desired ngram for all tweets passed in
        scoresAllTweets = self.getListOfScores(ngramsAllTweets)  #a list of scores for list of all ngrams passed in
                       
        lexiconFeatures = [{#pos scores
                            'total_count_pos': len(filter(true,map(greaterZeroBool,scores))),\
                            'total_score_pos': round(sum(filter(greaterZeroVal,scores)),3),\
                            'max_score_pos': round(max(map(greaterZeroVal,scores)),3),\
                            'score_last_pos':round(lastSentiScore(filter(greaterZeroVal,scores)),3),\
                            #neg scores
                            'total_count_neg': len(filter(true,map(lessZeroBool,scores))),\
                            'total_score_neg': round(sum(filter(lessZeroVal,scores)),3),\
                            'min_score_neg': round(min(map(lessZeroVal,scores)),3),\
                            'score_last_neg':round(lastSentiScore(filter(lessZeroVal,scores)),3)}\
                            for scores in scoresAllTweets]
        
        #print lexiconFeatures
        return lexiconFeatures 
        
        
class POScountExtractor(BaseEstimator, TransformerMixin):
    '''Adaptation of POS count features used in both NRC 2013/2014 Semeval submissions'''
    #TODO: Future work would consider both boolean and count values, currently only counts returned
    def __init__(self,posListKeyName = 'pos_token_list'):
        self.posListKeyName= posListKeyName #name of key containing list of pos tags

    def fit(self, x,y=None):
        return self

    def transform(self, transformedTweets):
        '''Transform list of transformed tweets in containing list of POS tags, returns desired dictionary format of POS counts'''   
        #print "POScountExtractor"
        #print transformedTweets           
        listOfPOSdicts = []
        
        for tweet in transformedTweets:
            #reset local POS dict
            localPOSdict = {'!': 0, '#': 0, '$': 0, '&': 0, ',': 0, 'A': 0,\
                '@': 0, 'E': 0, 'D': 0, 'G': 0, 'M': 0, 'L': 0, \
                'O': 0, 'N': 0, 'P': 0, 'S': 0, 'R': 0, 'U': 0,\
                 'T': 0, 'V': 0, 'Y': 0, 'X': 0, 'Z': 0, '^': 0, '~': 0}
            for tag in tweet[self.posListKeyName]:
                localPOSdict[tag] += 1
            listOfPOSdicts.append(localPOSdict)
        
        #print listOfPOSdicts
        return listOfPOSdicts
        
class NegationCountExtractor(BaseEstimator, TransformerMixin):
    '''For full details of how negation count is created see setTweetNegationVals in TweetTransformer.
    Returns list of dicts containing negation counts'''
    #TODO: Future work would further investigate with authors if the _NEG tag added to token was implemented with lexicons.  Based on research, there is no evidence this was implemented,
    #however wording in literature may indicate otherwise
    #NOTE: If you do want to include these in unigrams, perhaps consider adding the _NEG as a preprocessing step after NLP triple tagger
    
    def __init__(self,negationCountKeyName = 'negation_count'):
        self.negationCountKeyName= negationCountKeyName #name of key containing negation count value
        
    def fit(self, x,y=None):
        return self
        
    def transform(self, transformedTweets):
        '''Transform list of transformed tweets in containing list of POS tags, returns desired dictionary format of POS counts'''   
        #print "NegationcountExtractor"
        #print transformedTweets           
        listOfNegationCountdicts = []
        
        for tweet in transformedTweets:
            listOfNegationCountdicts.append( {self.negationCountKeyName: tweet[self.negationCountKeyName]})
        
        #print listOfNegationCountdicts
        return listOfNegationCountdicts
        
###---------------encoding transformers-------------###
class CapsCountExtractor(BaseEstimator, TransformerMixin):
    '''Adaptation of Capital count features used in both NRC 2013/2014 Semeval submissions
    Should count the total number of all caps words including hashtags for each tweet'''
    def __init__(self,tokenListKeyName= 'raw_token_list'):
        self.tokenListKeyName= tokenListKeyName #name of key containing tokens to search/count all caps
        
    def fit(self, x,y=None):
        return self

    def transform(self, transformedTweets):
        '''Transform list of Triples containing document/tweet triples to desired dictionary format of capitilized token counts'''      
        capsCountDicts = []
        for tweet in transformedTweets:   
            capsCountDicts.append({'total_count_caps':len(filter(lambda x: x.isupper(), tweet[self.tokenListKeyName]))} )
        return capsCountDicts


class HashCountExtractor(BaseEstimator, TransformerMixin):
    '''Adaptation of hashtag counts used in both NRC 2013/2014 Semeval submissions
    Should count the total number of hashtags for each tweet'''
    def __init__(self,posListKeyName= 'pos_token_list'):
        self.posListKeyName= posListKeyName #name of key containing tokens to search/count all caps

    def fit(self, x,y=None):
        return self

    def transform(self, transformedTweets):
        '''Transform list of Triples containing document/tweet triples to desired dictionary format of hashtag counts'''              
        hashtagCountDicts = []
        for tweet in transformedTweets:
            hashtagCountDicts.append({'total_count_hash':len(filter(lambda x: x=='#', tweet[self.posListKeyName]))})
        return hashtagCountDicts

class ElongWordCountExtractor(BaseEstimator, TransformerMixin):
    '''Adaptation of elongated word counts used in both NRC 2013/2014 Semeval submissions
    Should count the total number of words with more than 2 consecutive same characters (e.g. wooorld matches, woorld does not) for each tweet'''
    def __init__(self,tokenListKeyName= 'normalised_token_list'):
        self.tokenListKeyName= tokenListKeyName #name of key containing tokens to search/count all elongated words

    def fit(self, x,y=None):
        return self

    def transform(self, transformedTweets):
        '''Transform list of Triples containing document/tweet tokens to desired dictionary format of elongated counts'''              
        elongCountDicts = []
        regex = re.compile(r'(\w)\1{2,}')  #regex to match 3 or more repeating chars e.g. 'helllo' but not 'hello'
        for tweet in transformedTweets:
            elongCountDicts.append({'total_count_elong':len(filter(lambda token: token if ((regex.search(token)) !=None) else None,tweet[self.tokenListKeyName]))})
        return elongCountDicts
        

class PunctuationFeatureExtractor(BaseEstimator, TransformerMixin):
    '''Adaptation of punctuation feature extraction used in both NRC 2013/2014 Semeval submissions
    Should return counts where !!,!?,?? or more consecutive ! & ? occur and True if last token contains ! and True if last token contains ?'''
    def __init__(self,tokenListKeyName= 'normalised_token_list'):
        self.tokenListKeyName= tokenListKeyName #name of key containing tokens to search/count punctuation features
        
    def fit(self, x,y=None):
        return self

    def transform(self, transformedTweets):
        '''Transform list of Triples containing document/tweet tokens to desired dictionary format of elongated counts'''              
        punctuationCountDicts = []
        reExclaim = re.compile(r'!{2,}')  #regex to match consecutive exclamation marks
        reQuest = re.compile(r'\?{2,}')  #regex to match consecutive question marks
        reBoth = re.compile(r'(!\?|\?!){1,}')  #regex to match consecutive question marks
        for tweet in transformedTweets:
            pp = pprint.PrettyPrinter()
            print pp.pprint(tweet)
            try:
                punctuationCountDicts.append(
                {'count_contig_seq_exclaim':len(filter(lambda token: token if ((reExclaim.search(token)) !=None) else None,tweet[self.tokenListKeyName])),
                'count_contig_seq_question':len(filter(lambda token: token if ((reQuest.search(token)) !=None) else None,tweet[self.tokenListKeyName])),
                'count_contig_seq_both':len(filter(lambda token: token if ((reBoth.search(token)) !=None) else None,tweet[self.tokenListKeyName])),
                'last_toke_contain_quest':'?' in last(tweet[self.tokenListKeyName]),
                'last_toke_contain_exclaim':'!' in last(tweet[self.tokenListKeyName])
                })
            except:
                print tweet
            print pp.pprint(punctuationCountDicts)
        return punctuationCountDicts


#emoticon lexicons
class EmoticonExtractor(BaseEstimator, TransformerMixin):
    """Extract emoticon features from each tweet which can then be passed to DictVectorizer
    This transformer is an adaptation of papers/lexicons discussed in section 3 of
    http://www.saifmohammad.com/WebPages/lexicons.html
    Pass in a list of tweets/document triples extracted from twitter NLP and return emoticon features proposed in paper.
    NOTE: The KLUE emoticon dictionary has been used for these features as NRC authors did not provide a clear enough dictionary for 
    identifying pos/neg emoticons"""
    #TODO: Future work would try the regular expression used in Webis paper rather than lexicon
    def __init__(self,lexicon,tokenListKeyName= 'raw_token_list'):
        self.lexicon = lexicon #name of lexicon to use
        self.tokenListKeyName= tokenListKeyName #name of key containing tokens to search/count emoticon features

    def fit(self, x,y=None):
        return self

    def transform(self, transformedTweets):
        '''Transform list of Triples containing document/tweet tokens to desired vector format for specificied
         lexicon and options'''
        
        self.lexicon = helper.loadLexicon(self.lexicon)
        keyNames = set(self.lexicon.keys()) 
        
        emoticonFeatureDicts = []
        for tweet in transformedTweets:
            emoticonScores = map(lambda token: self.lexicon[token] if (token in keyNames)  else 0.0 ,tweet[self.tokenListKeyName])
            posBools = map(greaterZeroBool,emoticonScores)
            negBools = map(lessZeroBool,emoticonScores)  
            emoticonFeatureDicts.append({'positive_emoticon_present': any(posBools),\
                                'negative_emoticon_present': any(negBools),\
                                'last_emoticon_pos': last(posBools),\
                                'last_emoticon_neg':last(negBools)})
        return emoticonFeatureDicts
        
#clusters
class ClusterExtractor(BaseEstimator, TransformerMixin):
    '''Provided a list of transformed tweets  
    Extract a list of CMU cluster IDs
    As no python wrapper for the CMU tagger was found, this is a custom solution
    For more about the CMU cluster tagger see: http://www.ark.cs.cmu.edu/TweetNLP/
    The output CMUclusterIDlist can then be passed to count or tfidf vectorizer
        The lexicon was created from cmu cluster file.  3 steps give overview of how it was done.  Vocabulary file must be loaded into count/tfidf vectorizer for accurate counts
        see convertCMUorig.py in resources/scripts/CMUclusterScript/
        1- built a vocabulary to load into CountVectorizer should be 1000 cluster vals  Key = binary value Val = feature number
        2- created a lexicon/dictionary with key = token and val equal to binary value
        3- For each tweet build a string of binary cluster vals that can be split on string.split.   If token not in lexicon, add nothing to list
    '''
    def __init__(self,tokenListOfKeyNames= ['normalised_token_list']):
        self.tokenListOfKeyNames= tokenListOfKeyNames #name of key containing tokens to search for cluster ids, raw_token_list etc are also valid options
        
    def fit(self, x, y=None):
        return self
        
    def transform(self, transformedTweets):
        #print "ClusterExtractor"  
        #print transformedTweets  
        clusterLexicon =  helper.loadLexicon('cmu-cluster-lex')
        clusterWords = set(clusterLexicon.keys())
        CMUclusterIDlist = []  #list of id strings concatenated together and to return, each item in list is one tweet
        for tweet in transformedTweets:
            currentClusterList = []
            for tokenListKey in self.tokenListOfKeyNames:
                for token in tweet[tokenListKey ]:
                    if token in clusterWords:
                        currentClusterList.append(clusterLexicon[token])
            CMUclusterIDlist.append(' '.join(currentClusterList))
        #print CMUclusterIDlist
        return CMUclusterIDlist
        
#------KLUE FEATURES -----
#----token count----
class TokenCountExtractor(BaseEstimator, TransformerMixin):
    '''KLUE paper used token counts as feature, hence here it is implement.  Simply take the length of tweet triple.'''
    def __init__(self,tokenListKeyName= 'normalised_token_list'):
        self.tokenListKeyName= tokenListKeyName #name of key containing tokens to count
        
    def fit(self, x,y=None):
        return self

    def transform(self, transformedTweets):
        '''Transform list of Triples to a list of counts of token'''      
        #print "TokenCountExtractor"
        #print transformedTweets
        tokenCountDicts = []
        for tweet in transformedTweets: 
            tokenCountDicts.append({'token_count':len(tweet[self.tokenListKeyName])} )
        #print tokenCountDicts
        return tokenCountDicts

class KLUEpolarityExtractor(BaseEstimator, TransformerMixin):
    """Extract emoticon features from each document which can then be passed to DictVectorizer
    This transformer is an adaptation of of the KLUE Semeval 2013 submission
    Pass in a list of tweets/document triples extracted from twitter NLP and desired polarity features for
    AFINN lexicon. Note: optional lexicons also include klue-both, klue-emoticon and klue-acronym.
    """
    def __init__(self,lexicon='klue-afinn',tokenListKeyName= 'stem_list'):
        self.lexicon = lexicon
        self.lex_orig = lexicon   #TODO:remove if this doesn't improve things
        self.tokenListKeyName= tokenListKeyName #name of key containing tokens to search lexicon default is stem_list per Webis paper, raw_token_list etc are also valid options


    def fit(self, x,y=None):
        return self

    def transform(self, transformedTweets):
        '''Transform list of tweets containing specified tweet tokens to desired vector format for specificied
        KLUE polarity dictionary converter'''
        #print "KLUEpolarityExtractor"
        #print transformedTweets
        self.lexicon = helper.loadLexicon(self.lexicon)
        keyNames = set(self.lexicon.keys()) 
        polarityFeatureDicts = []
        for tweet in transformedTweets:
            polarityScores = map(lambda token: self.lexicon[token] if (token in keyNames)  else 0.0 ,tweet[self.tokenListKeyName])
            posBools = map(greaterZeroBool,polarityScores)
            negBools = map(lessZeroBool,polarityScores)  
            numPos = len(filter(true,posBools))
            numNeg = len(filter(true,negBools))
            numPolarTokens = numPos + numNeg
            if numPolarTokens == 0.0: #avoid division by zero
                numPolarTokens = 1.0
            totalScore = sum(polarityScores)
            meanScore = totalScore/(numPolarTokens)
            polarityFeatureDicts.append({'total_count_pos': numPos,\
                                'total_count_neg': numNeg,\
                                'total_count_polar': numPos + numNeg,\
                                'mean_polarity':meanScore})
        #print polarityFeatureDicts
        return polarityFeatureDicts   
        
#-----GUMLT FEATURES -----
class GUMLTsentiWordNetExtractor(BaseEstimator, TransformerMixin):
    """
    Converts a list of transformed tweet token lists into total positive and total negative scores retrieved from SentiWordNEt lexicon
    Per GUMLT Semeval 2013 and Webis 2015 papers
    """
    def __init__(self,lexicon='SentiWord',tokenListKeyName= 'negated_token_list'):
        self.lexicon = lexicon
        self.tokenListKeyName= tokenListKeyName #name of key containing tokens to search lexicon

    def fit(self, x,y=None):
        return self

    def transform(self, transformedTweets):
        '''Transform list transformed tweets containing specified token list to desired vector format for specificied
        GUMLT format'''
        self.lexicon = helper.loadLexicon(self.lexicon)
        keyNames = set(self.lexicon.keys()) 
        polarityFeatureDicts = []
        for tweet in transformedTweets:
            posPolarityScores = map(lambda token: self.lexicon[token+'+'] if ((token+'+') in keyNames)  else 0.0 ,tweet[self.tokenListKeyName])
            negPolarityScores = map(lambda token: self.lexicon[token+'-'] if ((token+'-') in keyNames)  else 0.0 ,tweet[self.tokenListKeyName])
            polarityFeatureDicts.append({'sum_pos': sum(posPolarityScores),\
                                'sum_neg': sum(negPolarityScores)})
        return polarityFeatureDicts
