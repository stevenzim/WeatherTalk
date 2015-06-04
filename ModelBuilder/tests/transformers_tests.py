from nose.tools import *
import twxeety.transformers as transformer
import twxeety.helper as helper

listOfDicts = [{'doc': 'abc', 'triple': [0,5,6]}, {'doc': 'def', 'triple': [1,2,3]}]
#listOfTriples = [['text','pos','conf']]
listOfTriples1 = [[['?',',',.9]],[['word','N',.9]]]
listOfTriples2 = [[['hello','#',.9],['http://you.com','U',.9]],[['word','N',.9]]]


def test_docs_and_triples_extractor():
	'''test to confirm docs and triples are correctly extracted from list of dicts'''
	d = transformer.DocsAndTriplesExtractor()
	docs,triples = d.transform(listOfDicts,'doc','triple')
	assert_equal(docs,['abc','def'])
	assert_equal(triples,[[0,5,6],[1,2,3]])

def test_text_features_extractor():
	'''test to confirm features are correctly extracted from triples'''
	d = transformer.TextFeaturesExtractor()
	#test 1 - confirm question mark is True
	featureDict = d.transform(listOfTriples1)
	assert_equal(featureDict["questmark_present"],[True,False])
    assert_equal(featureDict["urloremail_present"],[False,False])
	assert_equal(featureDict["hashtag_present"],[False,False])
	#test 2 - confirm url,email and hashtag test true
	featureDict = d.transform(listOfTriples2)
	assert_equal(featureDict["questmark_present"],[False,False])
	assert_equal(featureDict["urloremail_present"],[True,False])
	assert_equal(featureDict["hashtag_present"],[True,False])
