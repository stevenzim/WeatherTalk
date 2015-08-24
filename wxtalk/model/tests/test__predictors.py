from nose.tools import *
from wxtalk.model import predictors
from wxtalk import helper

testTweet1 = [{"text":"Bad day :(",\
                "id":"test1"}]


testExpected1 = [{"text":"Bad day :(",\
                "id":"test1",\
                "s1_discrete":-1,\
                "s1_proba":[0.952, 0.041, 0.007],\
                "s2_discrete":-1,\
                "s2_proba":[0.789, 0.197, 0.014]}]
                
testTweet2 = [{"text":"Good day :)",\
                "id":"test2"}]

testExpected2 = [{"text":"Good day :)",\
                "id":"test2",\
                "s1_discrete":1,\
                "s1_proba":[0.003, 0.003, 0.994],\
                "s2_discrete":1,\
                "s2_proba":[0.008, 0.042, 0.95]}]

modelList = [predictors.NRCmodelMetaData,predictors.KLUEmodelMetaData]


def test_predictions():
    '''Test to confirm discrete and probabilitic predictions are returned for a provided list of tweets'''
    #test 1 - negative sentiment with 2 models
    results = predictors.makePredictions(modelList,testTweet1)
    assert_equal(results,testExpected1)
    #test 2 - positive sentiment with 2 models
    results = predictors.makePredictions(modelList,testTweet2)
    assert_equal(results,testExpected2)
