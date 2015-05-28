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
    def __init__(self):
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

        #Twitter normalization vars
        self.TweetURLText = None        #tweet with URLs normalised
        self.TweetUserText = None       #tweet with usernames normalised
        self.TweetRepeatCharText = None #tweet with repeated chars normalised
        self.normalisedTweet = None     #fully normalised tweet with all options
    

        self.concatText = None          #concatenation of two desired keys
                                        #e.g. title + body		

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
        
    #twitter normalisation funcs
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

								

		
