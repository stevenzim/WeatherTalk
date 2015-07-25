from nose.tools import *
from wxtalk.model import predictors
from wxtalk import helper

testTweet1 = [{"text":"Bad day :(",\
                "id":"test1"}]

testExpected1 = [{"text":"Bad day :(",\
                "id":"test1",\
                "model_preds":{
                    "s1_discrete":-1,\
                    "s1_proba":[.9,.05,.05],\
                    "s2_discrete":-1,\
                    "s2_proba":[.8,.05,.15]}}]
                

testTweet2 = [{"text":"Good day :)",\
                "id":"test2"}]
testExpected2 = [{"text":"Good day :)",\
                "id":"test2",\
                "model_preds":{
                    "s1_discrete":1,\
                    "s1_proba":[.05,.05,.9],\
                    "s2_discrete":-1,\
                    "s2_proba":[.15,.05,.8]}}]


modelList = [predictors.model1MetaData,predictors.model2MetaData]


def test_predictions():
    '''Test to confirm discrete and probabilitic predictions are returned for a provided list of tweets'''
    #test 1 - negative sentiment with 2 models
    results = predictors.makePredictions(modelList,testTweet1)
    assert_equal(results,testExpected1)
    #test 2 - positive sentiment with 2 models
    results = predictors.makePredictions(modelList,testTweet2)
    assert_equal(results,testExpected2)
