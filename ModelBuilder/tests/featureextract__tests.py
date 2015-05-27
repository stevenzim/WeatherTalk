from nose.tools import *
import raop.featureextract.featureextract as featureextract
from nltk.tokenize import word_tokenize

def testEvidence():
    '''Test for find evidence function'''
    testTextEvi_true = "This is the state of my refrigerator: [Linky](http://i.imgur.com/JRvYJ5s.jpg)"
    testTextEvi_false = "http://www.4chan.org was not my favorite website "
  
    featObj = featureextract.FeatureExtract()
    featObj.findEvidence(testTextEvi_true)
    assert_equal(featObj.evidence,1)
    featObj.findEvidence(testTextEvi_false)
    assert_equal(featObj.evidence,0)
     
def testStatus():
    '''Test for status evaluation function'''
    featObj = featureextract.FeatureExtract()
    featObj.evalStatus(56,365.123,0,0)
    assert_equal(featObj.statusKarma,56)
    assert_equal(featObj.statusAccAge,365.123)
    assert_equal(featObj.statusPrevAct,0)
    featObj.evalStatus(-56,1.0000,3,6)
    assert_equal(featObj.statusKarma,-56)
    assert_equal(featObj.statusAccAge,1.0000)
    assert_equal(featObj.statusPrevAct,1)

def testNarratives():
    test_text = "Hi I am in need of food for my 4 children we are a military family that has really hit hard times and we have exahusted all means of help just to be able to feed my family and make it through another night is all i ask i know our blessing is coming so whatever u can find in your heart to give is greatly appreciated"
  
    featObj = featureextract.FeatureExtract()
    featObj.identifyNarratives(test_text)
    assert_equal(featObj.narrativeCountMoney1,0)
    assert_equal(featObj.narrativeCountMoney2,2)
    assert_equal(featObj.narrativeCountJob,0)
    assert_equal(featObj.narrativeCountFamily,3)

    featObj.countWord(word_tokenize(test_text))
    featObj.getMedianlist([{"added_Title_+_Request":test_text,"added_tokens":word_tokenize(test_text)}])
    featObj.identifyNarrativesBinary(test_text,featObj.wordNum)
    assert_equal(featObj.narrativeCountMoney1Bin,0)
    assert_equal(featObj.narrativeCountMoney2Bin,1)
    assert_equal(featObj.narrativeCountJobBin,0)
    assert_equal(featObj.narrativeCountFamilyBin,0)

def testReciprocity():
    testRecipro_text = " hi, i will pay it forward and return the favor wich will be doing reciprocity"
    
    featObj = featureextract.FeatureExtract()
    featObj.identifyReciprocity(testRecipro_text)
    assert_equal(featObj.findReciprocity,1)

def testWordCount() :
    '''test wordcount'''
    testTokens = ['there','are','four','words']
    featObj = featureextract.FeatureExtract()
    featObj.countWord(testTokens)
    assert_equal(featObj.wordNum, 4)

def testTime() :
    '''test time'''
    testInput=1297722537.0 
    featObj = featureextract.FeatureExtract()
    featObj.getMinTime([{"unix_timestamp_of_request":1297722537.0 }])
    featObj.getTime(testInput)
    assert_equal(featObj.time, 1297722537.0 -featObj.minTime)

def testfirstHalf():
    '''first half'''
    testInput=1317852607.0
    featObj = featureextract.FeatureExtract()
    featObj.getFirstHalf(testInput)
    assert_equal(featObj.firstHalf,1)
    
def testPOSTag():
    testTags = [['Thanks','NNP'],['good','JJ'],['super','JJS']]
    featObj = featureextract.FeatureExtract()
    tagCount = featObj.CountPOSTag(testTags, 'JJ')
    assert_equal(tagCount, 2)   


