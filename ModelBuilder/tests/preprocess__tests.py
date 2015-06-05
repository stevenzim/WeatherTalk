from nose.tools import *
import twxeety.preprocess.preprocess as preprocess
import twxeety.helper as helper

#TODO: REVIEW THIS WHEN PROTOTYPE COMPLETE MOST (IF NOT ALL) CAN BE REMOVED
testTwitterDict1 = {'text' : "@RasmussenPoll01 http://link1.com https://link2.com haaaappppy!"}
listOfTweetDicts = helper.loadJSONfromFile("test-data/postTweetNLP-test.json")
testTriple1 = listOfTweetDicts[0]["tagged_tweet_triples"]
testTriple2 = listOfTweetDicts[1]["tagged_tweet_triples"]

#added twitter features
def test_twitter_norm():
    '''Test for normalisation of twitter specific text
    These are basic normalisation components per non Semeval papers'''
    preProcObj = preprocess.Preprocess()
    #componenent normalisation tests
    preProcObj.convertTwitterURL('http://link1.com')
    preProcObj.convertTwitterUser('@RasmussenPoll01')
    preProcObj.convertTwitterRepeatedChar('haapppyyyy')
    assert_equal(preProcObj.TweetURLText,'URL')
    assert_equal(preProcObj.TweetUserText,'USER')
    assert_equal(preProcObj.TweetRepeatCharText,'haappyy')
    #full normalisation of tweet test 
    preProcObj.normaliseTweet(testTwitterDict1['text'])
    assert_equal(preProcObj.normalisedTweet,'USER URL URL haappy!')
    
#added twitter features from SemEval paper e.g. rtrgo
def test_set_norm_tokens_rtrgo():
    '''Test method to extract tokens from triple and store in seperate list'''
    #first test to verify non-normalised tokens are loaded into lists
    #1a test to ensure triple loaded properly and tokens and pos tags returned as list
    preProcObj = preprocess.Preprocess(tweet_triples = testTriple1)
    preProcObj.setNotNormalTokens()
    assert_equal(preProcObj.not_normal_tokens_rtrgo,["I","am","you","?"])
    assert_equal(preProcObj.pos_tweet_tags,["O","V","O",","])
    #1b test to verify hashtag, url/email and question mark boolean values setDictionary
    #test set 1
    assert_equal(preProcObj.hashtag_present,False)
    assert_equal(preProcObj.urloremail_present,False)
    assert_equal(preProcObj.questmark_present,True)
    #test set 2
    preProcObj2 = preprocess.Preprocess(tweet_triples = testTriple2)
    preProcObj2.setNotNormalTokens()
    assert_equal(preProcObj2.hashtag_present,True)
    assert_equal(preProcObj2.urloremail_present,True)
    assert_equal(preProcObj2.questmark_present,False) 
    
    #second test to verify normalisation of tokens per RTRGO
    #2a pass in existing object that has list  tokens
    preProcObj.setNormalTokensRTRGO(preProcObj.not_normal_tokens_rtrgo)
    assert_equal(preProcObj.normal_tokens_rtrgo,["i","am","you","?"])
    #2b pass in list of tokens
    preProcObj.setNormalTokensRTRGO(["I","am","you",".","#HAPPPYYYY"])
    assert_equal(preProcObj.normal_tokens_rtrgo,["i","am","you",".","happpyyyy"])
    #2c verify string concatenation of normalised tokens
    assert_equal(preProcObj.normal_string_rtrgo,"i am you . happpyyyy")
    
    #componenent normalisation tests
#    preProcObj.convertTwitterURL('http://link1.com')
#    preProcObj.convertTwitterUser('@RasmussenPoll01')
#    preProcObj.convertTwitterRepeatedChar('haapppyyyy')
#    assert_equal(preProcObj.TweetURLText,'URL')
#    assert_equal(preProcObj.TweetUserText,'USER')
#    assert_equal(preProcObj.TweetRepeatCharText,'haappyy')
#    #full normalisation of tweet test 
#    preProcObj.normaliseTweet(testTwitterDict1['text'])
#    assert_equal(preProcObj.normalisedTweet,'USER URL URL haappy!')




#original features from raop

testDict = {'text' : 'I am here.'}
testDict2 = {'text' : 'I am doing the tests.',
	     'title' : 'TESTING'}
testDict3 = {'text' : 'I am here. I will be home soon.'}

def test_set_dict():
	'''Test to load dictionary'''
	preProcObj = preprocess.Preprocess()
	preProcObj.setDictionary(testDict)
	assert_equal(preProcObj.kaggleDict,testDict)


def test_tokenize():
	'''Test for word tokenizer'''
	preProcObj = preprocess.Preprocess()
	preProcObj.setDictionary(testDict)
	preProcObj.tokenize(preProcObj.kaggleDict.get('text'))
	assert_equal(preProcObj.tokenizedText, ['I', 'am', 'here', '.'])


def test_pos_tag():
	'''Test for pos tagger'''
	preProcObj = preprocess.Preprocess()
	preProcObj.setDictionary(testDict)
	preProcObj.tokenize(preProcObj.kaggleDict.get('text'))
	preProcObj.posTag(preProcObj.tokenizedText)
	assert_equal(preProcObj.POS_TaggedText , [('I', 'PRP'), ('am', 'VBP'), ('here', 'RB'), ('.', '.')])


def test_norm():
    '''Test for standard normalisation components'''
    preProcObj = preprocess.Preprocess()
    preProcObj.setDictionary(testDict2)
    preProcObj.tokenize(preProcObj.kaggleDict.get('text'))
    preProcObj.lowerCase(preProcObj.tokenizedText)
    preProcObj.stopWordRm(preProcObj.lowerCaseText)
    preProcObj.stem(preProcObj.stopWordRmText)
    assert_equal(preProcObj.lowerCaseText,['i', 'am', 'doing', 'the','tests','.'])
    assert_equal(preProcObj.stopWordRmText,['tests','.'])
    assert_equal(preProcObj.stemmedText,['test','.'])
    preProcObj.normalisation(preProcObj.tokenizedText)
    assert_equal(preProcObj.normalisedText,['test','.'])



def test_concat():
	'''Test for field concatenator'''
	preProcObj = preprocess.Preprocess()
	preProcObj.setDictionary(testDict2)
	preProcObj.concatenate('title', 'text')
	assert_equal(preProcObj.concatText, 'TESTING I am doing the tests.')

def test_drop_key():
	'''Test to drop key (and values) from dict'''
	preProcObj = preprocess.Preprocess()
	preProcObj.setDictionary(testDict2)
	preProcObj.dropKey('text')
	assert_equal(preProcObj.kaggleDict, {'title' : 'TESTING'})

def test_sen_split():
	'''Test for sentence spliting'''
	preProcObj = preprocess.Preprocess()
	preProcObj.setDictionary(testDict3)
	preProcObj.sentSeg(preProcObj.kaggleDict.get('text'))
	assert_equal(preProcObj.sentSegmentedText, ['I am here.', 'I will be home soon.'])
