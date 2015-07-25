from nose.tools import *
from wxtalk.model import ensemblers
from wxtalk import helper


testTweetWithPreds1 = [{"text":"Bad day :(",\
                "id":"test1",\
                "model_preds":{
                    "s1_discrete":-1,\
                    "s1_proba":[.2,.7,.1],\
                    "s2_discrete":-1,\
                    "s2_proba":[.8,.1,.1]}}]

expectedTweetWithPreds1 = [{"text":"Bad day :(",\
                            "id":"test1",\
                            "model_preds":{
                                "s1_discrete":-1,\
                                "s1_proba":[.2,.7,.1],\
                                "s2_discrete":-1,\
                                "s2_proba":[.8,.1,.1]},\
                            'ens_s1_discrete':-1,\
                            'ens_s1_prob':.5}]
expectedTweetWithPreds2 = [{"text":"Bad day :(",\
                            "id":"test1",\
                            "model_preds":{
                                "s1_discrete":-1,\
                                "s1_proba":[.2,.7,.1],\
                                "s2_discrete":-1,\
                                "s2_proba":[.8,.1,.1]},\
                            'ens_s2_discrete':0,\
                            'ens_s2_prob':.5}]
expectedTweetWithPreds3 = [{"text":"Bad day :(",\
                            "id":"test1",\
                            "model_preds":{
                                "s1_discrete":-1,\
                                "s1_proba":[.2,.7,.1],\
                                "s2_discrete":-1,\
                                "s2_proba":[.8,.1,.1]},\
                            'ens_s1_discrete':-1,\
                            'ens_s1_prob':.5,\
                            'ens_s2_discrete':0,\
                            'ens_s2_prob':.5}]
ensemble1params = {"id":'ens_s1',\
            "model_id_list":['s1','s2'],\
            "model_classes":[-1,0,1],\
            "description":"equal weighted ensemble between NRC/KLUE"}

ensemble2params = {"id":'ens_s2',\
            "model_id_list":['s1','s1','s2'],\
            "model_classes":[-1,0,1],\
            "description":"weighted ensemble 2/3 NRC + 1/3 KLUE"}

#TODO: Test for mismatch of len(model_classes) and len(model_proba)
#TODO: Test for mismatch/unavailability of model id

def test_ensembles():
    '''Test to confirm discrete class and probabilitic weighted average of that class is returned'''
    #test 1 - equalweights
    results = ensemblers.compileEnsemble([ensemble1params],testTweetWithPreds1)
    assert_equal(results,expectedTweetWithPreds1)
    #test 2 - non equalweights
    results = ensemblers.compileEnsemble([ensemble1params,ensemble2params],testTweetWithPreds1)
    assert_equal(results,expectedTweetWithPreds2)
    #test 3 - combined results
    results = ensemblers.compileEnsemble([ensemble1params,ensemble2params],testTweetWithPreds1)
    assert_equal(results,expectedTweetWithPreds3)

