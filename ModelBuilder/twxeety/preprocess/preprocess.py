'''
preprocess.py

Preprocessing module for textual data from Kaggle competition.  The module
allows you to pass in a dictionary of various fields.  Funcationality allows for
fields to be dropped from the dict.  Most importantly, the text fields can be 
processed with the nltk library methods including tokenizer, pos tagging,
word stemming as well as several other options.
'''


from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.stem.porter import *
from nltk.corpus import stopwords
import re


class Preprocess(object):
    def __init__(self,tweet_triples = None):
        '''Initialize the preprocessing class'''
        self.kaggleDict = {}            #dictionary passed in
        self.sentSegmentedText = None   #segment sentences for counting
        self.tokenizedText = None       #tokenized text
        self.POS_TaggedText = None      #tagged tokens e.g. adjective, adverb
		
		#Text normalization variables
        self.lowerCaseText = None       #text to lower case
        self.stopWordRmText = None      #stopwords removed e.g. the, and
        self.stemmedText = None         #stemmed text e.g. running-->run
        self.normalisedText = None      #normalized text e.g. 'and Running'->run

        #Twitter normalization vars (popular amongst many papers)
        self.TweetURLText = None        #tweet with URLs normalised
        self.TweetUserText = None       #tweet with usernames normalised
        self.TweetRepeatCharText = None #tweet with repeated chars normalised
        self.normalisedTweet = None     #fully normalised tweet with all options
        
        #Twitter normalization/feature extraction vars adapted from RTRGO 
        '''See Semeval2014 conference proceeding RTRGO: enghancing the GU-MLT-LT
        System for Sentiment Analysis of Short Messages 
        & twitterNLP from Carnegie Mellon'''
        self.tagged_tweet_triples = tweet_triples #As extracted by the tweet tagger 
                                                  #developed at carnegie mellon
                                                  #see Paper by Owoputi et. al 2013
                                                  #NOTE: These are stored in a dictionary
                                                  # via twxeety.pipeline.extractTweetNLPtriples
        self.not_normal_tokens_rtrgo = None #Pre-normalised tokens listOfTokensTags
        self.pos_tweet_tags = None          #POS tags from triples returned from twitterNLP
        self.pos_tweet_tag_conf = None      #Confidence score for POS tag from twitterNLP
        self.normal_tokens_rtrgo = None     #Normalised tokens per RTRGO paper
        self.normal_string_rtrgo = None     #Concatenation of list items in normal_tokens_rtrgo
                                            #This is used to simplify the vectorization process
                                            #in scikit learn
        self.hashtag_present = False        #If hashtag present in Tweet, then true
        self.urloremail_present = False     #If URL/Email present in Tweet, then true
        self.questmark_present = False      #If question mark token present in Tweet, then true
                                          
                           

    

        self.concatText = None          #concatenation of two desired keys
                                        #e.g. title + body		

    #twitter normalization/feature extraction based on RTRGO papers
    #TODO: Consider additional normalisation and features per paper, 
    #       1 - currently only removing # and convert to lowercase
    #       2 - Don't yet know how to remove punctuation and tokens from bigrams so not doing that
    #       3 - Not using word stems or clusters
    #       4 - Not using a sentiment lexicon yet
    #       5 - Not implementing anything else below sentiment lexica
    
    def setNotNormalTokens(self):
        '''With list of tweetNLP tag triples set, creates a list of non-normalised tokens'''
        #TODO: consider refactor of this function.  It is likely we could just put everything in normalising function,
        #       However, this is a good basic token list, which could go down various paths of normalisation
        #       Optionally, this could become a very generic function, where the specified triple value is passed including
        #       triple[0] = token, triple[1] = POS, triple[2] = likelihood score
        #
        if self.tagged_tweet_triples != None:
            tempTokenList = []
            tempPOSList = []
            tempConfList = []
            for triple in self.tagged_tweet_triples:
                tempTokenList.append(triple[0])
                tempPOSList.append(triple[1])
                tempConfList.append(triple[2])
                #dirty feature extract
                #TODO: Put feature extraction in seperate method, just need to get something working
                #set hashtag feature
                if triple[1] == '#':
                    self.hashtag_present = True
                #set url/email feature 
                if triple[1] == 'U':
                    self.urloremail_present = True
                #set question mark feature
                if triple[0] == '?':
                    self.questmark_present = True
            self.not_normal_tokens_rtrgo = tempTokenList
            self.pos_tweet_tags = tempPOSList
            self.pos_tweet_tag_conf = tempConfList   #Not used or tested currently  Perhaps consider later

    def setNormalTokensRTRGO(self, nonNormalTokenList):
        '''Given list of tweetNLP non-normalised tokens, normalise tokens per RTRGO'''
        tempTokenList = []
        for token in nonNormalTokenList:
            tempToken = token.lower()
            tempToken = tempToken.replace("#","")
            tempTokenList.append(tempToken) 
        self.normal_tokens_rtrgo = tempTokenList
        #concatenat normalized token list into string with spaces in between
        #this is done for simplification of vectorization process in scikit learn
        self.normal_string_rtrgo = ' '.join(tempTokenList)
        

    #twitter normalisation funcs (ORIGINALs before Semeval papers e.g. RTRGO)
    def convertTwitterURL(self, textString):
        '''Converts all URLs in tweet to "URL" It has been shown in 
        multiple papers that this is an important preprocessing step'''
        textString = re.sub(r'https?:\/\/.\S+', "URL",textString)
        self.TweetURLText = textString

    def convertTwitterUser(self, textString):
        '''Converts all usernames in tweet to "USER" It has been shown in 
        multiple papers that this is an important preprocessing step
        e.g. @DavidCameron becomes USER'''
        textString = re.sub(r'@\S+', "USER",textString)
        self.TweetUserText = textString 

    def convertTwitterRepeatedChar(self, textString):
        '''
        Converts all alpha-num characters repeated 3 or more times down to 2 
        in tweet. It has been shown in multiple papers that this  can be useful
        for improved performance.  There are discrepencies as to the number of
        characters to remove (e.g. more than 3 becomes 3 vs 3 or more becomes 2
        example:  "Moonnnnneyyyy!!!!" becomes "Moonneyy!!!!"
        '''
        textString =  re.sub(r'(.)\1+', r'\1\1',textString)
        self.TweetRepeatCharText = textString


    def normaliseTweet(self, textString):
        '''Run all normalisation functions on tweet text string.'''
        print textString
        self.convertTwitterURL(textString)
        self.convertTwitterUser(self.TweetURLText)
        self.convertTwitterRepeatedChar(self.TweetUserText)
        self.normalisedTweet=self.TweetRepeatCharText

    ######original raop functions  TODO: some of these could be removed
    def setDictionary(self,dictionary):
        '''Sets the dictionary'''
        self.kaggleDict = dictionary
	
    def sentSeg(self, textString):
        '''Splits the string of text into individual sentences, 
        returns a list of sentences'''
        self.sentSegmentedText = sent_tokenize(textString) 

    def tokenize(self,textString):
        '''Tokenize a text string using standard nltk tokenizer'''
        self.tokenizedText = word_tokenize(textString)

    def posTag(self, tokens):
        '''POS tag a list of tokenized text using standard nltk POS tagger'''
        self.POS_TaggedText = pos_tag(tokens)

    def lowerCase(self, tokens):
        '''Convert tokens to lowercase'''
        self.lowerCaseText = [w.lower() for w in tokens ]

    def stopWordRm(self, tokens):
        '''Remove stop words from list of tokens'''
        wstop = stopwords.words('english')	
        self.stopWordRmText = [w for w in tokens if w not in wstop]

    def stem(self, tokens):
        '''Run porter stemmer on list of tokens'''
        stemmer = PorterStemmer()
        self.stemmedText=[stemmer.stem(w) for w in tokens ]

    def normalisation(self, tokens):
        '''Run all normalisation functions on list of tokens'''
        self.lowerCase(tokens)
        self.stopWordRm(self.lowerCaseText)
        self.stem(self.stopWordRmText)
        self.normalisedText=self.stemmedText

    def concatenate(self, firstKey, secondKey):
        '''Concatenate two string key value pairs from dictionary
        First Key Values + Second Key Values.
        The encoding string encoding is necessary for string concatenation.
        The decoding is necessary for the string to be dumped back to JSON'''
        self.concatText = (str (self.kaggleDict.get(firstKey).encode('utf-8') +\
         ' ' + self.kaggleDict.get(secondKey).encode('utf-8'))).decode('utf-8')

    def dropKey(self, keyName):
        '''Remove specified Key Value from dictionary'''
        self.kaggleDict.pop(keyName)
        


								

		
