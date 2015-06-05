from nose.tools import *
import twxeety.transformers as transformer
import twxeety.helper as helper

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
    d = transformer.TriplesYsExtractor()
    triples = d.transform(listOfDicts,'triple')
    assert_equal(triples,[[0,5,6],[1,2,3]])
    #test 2, triples and ys
    d = transformer.TriplesYsExtractor()
    triples, ys = d.transform(listOfDicts,'triple','expect')
    assert_equal(triples,[[0,5,6],[1,2,3]])
    assert_equal(ys,[True,False])

def test_docs_extractor():
    '''Test to confirm list of normalised docs are returned provided triples containing tokens'''
    d = transformer.DocsExtractor()
    #no docs test
    assert_equal(d.transform([]),[])
    #single doc test
    assert_equal(d.transform(listOfTriples2),['hello woorrlld'])
    #multiple docs test
    assert_equal(d.transform(listOfTriples3),['hello woorrlld','hello woorrlld'])    

def test_text_features_extractor():
    '''test to confirm features are correctly extracted from triples'''
    d = transformer.TextFeaturesExtractor()
    featureDict = d.transform(listOfTriples1)
    assert_equal(featureDict[0],listOfDocsFeats[0]) #doc1 has question mark
    assert_equal(featureDict[1],listOfDocsFeats[1]) #doc2 has url and hashtag

