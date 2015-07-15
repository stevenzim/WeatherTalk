from nose.tools import *
from wxtalk.modelbuilder import transformers
from wxtalk import helper

listOfDicts = [{'doc': 'abc', 'triple': [0,5,6],'expect':True},\
                 {'doc': 'def', 'triple': [1,2,3],'expect':False}]
listOfTriples1 = [[['?',',',.9]],\
                   [['hello','#',.9],['http://you.com','U',.9]]] #doc 2
doc1features = {"questmark_present":True,
                "urloremail_present":False,
                "hashtag_present":False}
doc2features = {"questmark_present":False,
                "urloremail_present":True,
                "hashtag_present":True}
listOfDocsFeats = [doc1features,doc2features]

listOfTriples2 = [[['#Hello','#',.9],['Woorrlld','N',.9]]]
listOfTriples3 = [listOfTriples2[0],listOfTriples2[0]]


def test_triples_and_ys_extractor():
    '''test to confirm triples and ys(expected output) are correctly extracted from list of dicts'''
    #test 1, triples only
    d = transformers.TriplesYsExtractor()
    triples = d.transform(listOfDicts,'triple')
    assert_equal(triples,[[0,5,6],[1,2,3]])
    #test 2, triples and ys
    d = transformers.TriplesYsExtractor()
    triples, ys = d.transform(listOfDicts,'triple','expect')
    assert_equal(triples,[[0,5,6],[1,2,3]])
    assert_equal(ys,[True,False])

def test_docs_extractor():
    '''Test to confirm list of normalised docs are returned provided triples containing tokens'''
    d = transformers.DocsExtractor()
    #no docs test
    assert_equal(d.transform([]),[])
    #single doc test
    assert_equal(d.transform(listOfTriples2),['hello woorrlld'])
    #multiple docs test
    assert_equal(d.transform(listOfTriples3),['hello woorrlld','hello woorrlld'])    

def test_text_features_extractor():
    '''test to confirm features are correctly extracted from triples'''
    d = transformers.TextFeaturesExtractor()
    featureDict = d.transform(listOfTriples1)
    #test1 - all features test
    assert_equal(featureDict[0],listOfDocsFeats[0]) #doc1 has question mark
    assert_equal(featureDict[1],listOfDocsFeats[1]) #doc2 has url and hashtag
    #test2 -question and urlemail removed
    featureDict = d.transform(listOfTriples1,['questmark_present',"urloremail_present"])
    assert_equal(featureDict[0],{"hashtag_present":False})
    assert_equal(featureDict[1],{"hashtag_present":True})


#lexicon tests
listOfTriples4 = [[['#Hello','#',.9],['world','N',.9]]]
#140
#    "world": "0.551",
nrc140FeaturesUnigrams = {'total_count_posi':1,
                     'total_score':.551,
                     'max_score':.551,
                     'score_last_posi_token':.551}
                     
#hash
#    "#hello": "2.018",
#    "world": "0.384",
nrcHashFeaturesUnigrams = {'total_count_posi':2,
                     'total_score':2.402,
                     'max_score':2.018,
                     'score_last_posi_token': 0.384}
                     
def test_nrc_140_features_extractor():
    '''test to confirm NRC 140 lexicon features are correctly extracted from triples'''
    d = transformers.NRCLexiconsExtractor(lexicon = 'NRC140',gramType = 'unigram',tagType = 'token')
    featureDict = d.transform(listOfTriples4)
    #test1 - unigrams/single doc/NRC140
    assert_equal(featureDict[0],nrc140FeaturesUnigrams) 
                   
def test_nrc_hash_features_extractor():
    '''test to confirm NRC 140 lexicon features are correctly extracted from triples'''
    d = transformers.NRCLexiconsExtractor(lexicon = 'NRCHash',gramType = 'unigram',tagType = 'token')
    featureDict = d.transform(listOfTriples4,)
    #test1 - unigrams/single doc/NRCHash
    assert_equal(featureDict[0],nrcHashFeaturesUnigrams)

#def test_nrc_140_features_extractor():
#    '''test to confirm NRC 140 lexicon features are correctly extracted from triples'''
#    d = transformers.NRCLexiconsExtractor(lexicon = 'NRC140')
#    featureDict = d.transform(listOfTriples4,lexicon = 'NRC140',gramType = 'unigram',tagType = 'token')
#    #test1 - unigrams/single doc/NRC140
#    assert_equal(featureDict[0],nrc140FeaturesUnigrams) 
#                   
#def test_nrc_hash_features_extractor():
#    '''test to confirm NRC 140 lexicon features are correctly extracted from triples'''
#    d = transformers.NRCLexiconsExtractor(lexicon = 'NRC140')
#    featureDict = d.transform(listOfTriples4,lexicon = 'NRCHash',gramType = 'unigram',tagType = 'token')
#    #test1 - unigrams/single doc/NRCHash
#    assert_equal(featureDict[0],nrcHashFeaturesUnigrams)
    
    

