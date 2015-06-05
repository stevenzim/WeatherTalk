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



def test_docs_and_triples_extractor():
	'''test to confirm docs and triples are correctly extracted from list of dicts'''
	#test 1, docs and triples only
	d = transformer.DocsTriplesYsExtractor()
	docs,triples = d.transform(listOfDicts,'doc','triple')
	assert_equal(docs,['abc','def'])
	assert_equal(triples,[[0,5,6],[1,2,3]])
	#test 2, docs, triples and ys(e.g. expected results)
	d = transformer.DocsTriplesYsExtractor()
	docs,triples,ys = d.transform(listOfDicts,'doc','triple','expect')
	assert_equal(docs,['abc','def'])
	assert_equal(triples,[[0,5,6],[1,2,3]])
	assert_equal(ys,[True,False])

def test_text_features_extractor():
    '''test to confirm features are correctly extracted from triples'''
    d = transformer.TextFeaturesExtractor()
    featureDict = d.transform(listOfTriples1)
    assert_equal(featureDict[0],listOfDocsFeats[0]) #doc1 has question mark
    assert_equal(featureDict[1],listOfDocsFeats[1]) #doc2 has url and hashtag

