from nose.tools import *
import twxeety.preprocess.preprocess as preprocess


testDict = {'text' : 'I am here.'}
testDict2 = {'text' : 'I am doing the tests.',
	     'title' : 'TESTING'}
testDict3 = {'text' : 'I am here. I will be home soon.'}
testTwitterDict1 = {'text' : "@RasmussenPoll01 http://link1.com https://link2.com haaaappppy!"}

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

     
def test_twitter_norm():
    '''Test for normalisation of twitter specific text'''
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
