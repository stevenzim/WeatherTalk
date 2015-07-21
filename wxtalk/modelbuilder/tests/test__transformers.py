from nose.tools import *
from wxtalk.modelbuilder import transformers
from wxtalk import helper


    

def test_porter_stemmer():
    '''Test porter stemmer'''
    doc = ['lovely jubbly']
    d = transformers.StemExtractor()
    #test1 1 doc
    stems = d.transform(doc)
    assert_equal(stems,['love jubbl'])
    #test1 2 docs
    stems = d.transform([doc[0],doc[0]])
    assert_equal(stems,['love jubbl','love jubbl'])


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

listOfTriplesURL = [[['https://hello.com','U',.9],['http://hello.com','U',.9]]]
listOfTriplesUSER = [[['@me','@',.9],['@you','@',.9]]]

triplesToNegate1 = [{"tagged_tweet_triples":[['No','a',.9],['!','.',.9],['Yes','a',.9],['snow','a',.9],['!','.',.9]]}]
expectedNegation1 =[[['No_NEG','a',.9],['!','.',.9],['Yes','a',.9],['snow','a',.9],['!','.',.9]]]

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
    #test 3, negate tokens intriples and ys
    d = transformers.TriplesYsExtractor(negateTweet=True)
    triples= d.transform(triplesToNegate1)
    assert_equal(triples,expectedNegation1)


def test_docs_extractor():
    '''Test to confirm list of normalised docs are returned provided triples containing tokens'''
    d = transformers.DocsExtractor()
    #no docs test
    assert_equal(d.transform([]),[])
    #single doc test
    assert_equal(d.transform(listOfTriples2),['hello woorrlld'])
    #multiple docs test
    assert_equal(d.transform(listOfTriples3),['hello woorrlld','hello woorrlld'])    
    #URL test
    assert_equal(d.transform(listOfTriplesURL),['URL URL'])
    #USER test
    assert_equal(d.transform(listOfTriplesUSER),['USER USER'])

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


####----lexicon tests
listOfTriples4 = [[['#Hello','#',.9],['world','N',.9]]]
listOfTriples5 = [[['ADORE','V',.9],['him','N',.9],['back','N',.9]]]
listOfNegatedTriples4 = [[['#Hello_NEG','#',.9],['world_NEG','N',.9]]]
listOfNegatedTriples5 = [[['ADORE_NEG','V',.9],['him_NEG','N',.9],['back_NEG','N',.9]]]

####manual lexicons
#bing and liu / listOfTriples5
#    "adore": 1.0,
bingLiuFeatures ={'total_count_pos':1,
                 'total_score_pos':1.0,
                 'max_score_pos':1.0,
                 'score_last_pos':1.0,
                 'total_count_neg':0,
                 'total_score_neg':0.0,
                 'min_score_neg':0.0,
                 'score_last_neg':0.0}
#MPQA / listOfTriples5
#    "adore": 1.0,
#    "back": 1.0,
mpqaFeatures ={'total_count_pos':2,
                 'total_score_pos':6.0,
                 'max_score_pos':5.0,
                 'score_last_pos':1.0,
                 'total_count_neg':0,
                 'total_score_neg':0.0,
                 'min_score_neg':0.0,
                 'score_last_neg':0.0}
                     
#NRC emotions / listOfTriples5
#    "adore": 1.0,
nrcEmotionFeatures ={'total_count_pos':1,
                 'total_score_pos':1.0,
                 'max_score_pos':1.0,
                 'score_last_pos':1.0,
                 'total_count_neg':0,
                 'total_score_neg':0.0,
                 'min_score_neg':0.0,
                 'score_last_neg':0.0}

def test_manual_lexicon_features_extractor():
    '''test to confirm NRC 140 lexicon features are correctly extracted from triples'''
    #test1 - single doc/BingLiu
    d = transformers.NRCLexiconsExtractor(lexicon = 'BingLiu')
    featureDict = d.transform(listOfTriples5)
    assert_equal(featureDict[0],bingLiuFeatures) 
    #test2 - single doc/MPQA
    d = transformers.NRCLexiconsExtractor(lexicon = 'MPQA')
    featureDict = d.transform(listOfTriples5)
    assert_equal(featureDict[0],mpqaFeatures) 
    #test3 - single doc/NRCemotions
    d = transformers.NRCLexiconsExtractor(lexicon = 'NRCemotion')
    featureDict = d.transform(listOfTriples5)
    assert_equal(featureDict[0],nrcEmotionFeatures) 
    #test4 - single doc/NRCemotions - confirm same score for negated triples
    d = transformers.NRCLexiconsExtractor(lexicon = 'NRCemotion')
    featureDict = d.transform(listOfNegatedTriples5)
    assert_equal(featureDict[0],nrcEmotionFeatures) 


####automatic lexicons
#140 / listOfTriples4
#    "world": "0.551",
nrc140FeaturesUnigrams = {'total_count_pos':1,
                 'total_score_pos':.551,
                 'max_score_pos':.551,
                 'score_last_pos':.551,
                 'total_count_neg':0,
                 'total_score_neg':0.0,
                 'min_score_neg':0.0,
                 'score_last_neg':0.0}


                     
#140 bigrams / listOfTriples5
#    "adore him": "1.435",
#    "him back": "-0.566",
nrc140FeaturesBigrams = {'total_count_pos':1,
                 'total_score_pos':1.435,
                 'max_score_pos':1.435,
                 'score_last_pos':1.435,
                 'total_count_neg':1,
                 'total_score_neg':-0.566,
                 'min_score_neg':-0.566,
                 'score_last_neg':-0.566}


def test_nrc_140_features_extractor():
    '''test to confirm NRC 140 lexicon features are correctly extracted from triples'''
    #test1 - unigrams/single doc/NRC140
    d = transformers.NRCLexiconsExtractor(lexicon = 'NRC140',gramType = 'unigram',tagType = 'token')
    featureDict = d.transform(listOfTriples4)
    assert_equal(featureDict[0],nrc140FeaturesUnigrams) 
    #test2 - bigrams/single doc/NRC140
    d = transformers.NRCLexiconsExtractor(lexicon = 'NRC140',gramType = 'bigram',tagType = 'token')
    featureDict = d.transform(listOfTriples5)
    assert_equal(featureDict[0],nrc140FeaturesBigrams) 
                                                   

#hash  / listOfTriples4
#    "#hello": "2.018",
#    "world": "0.384",
nrcHashFeaturesUnigrams = {'total_count_pos':2,
                 'total_score_pos':2.402,
                 'max_score_pos':2.018,
                 'score_last_pos':0.384,
                 'total_count_neg':0,
                 'total_score_neg':0.0,
                 'min_score_neg':0.0,
                 'score_last_neg':0.0}

      

def test_nrc_hash_features_extractor():
    '''test to confirm NRC 140 lexicon features are correctly extracted from triples'''
    d = transformers.NRCLexiconsExtractor(lexicon = 'NRCHash',gramType = 'unigram',tagType = 'token')
    featureDict = d.transform(listOfTriples4)
    #test1 - unigrams/single doc/NRCHash
    assert_equal(featureDict[0],nrcHashFeaturesUnigrams)


#POS count tests
posCountsTriples5 = {'!': 0, '#': 0, '$': 0, '&': 0, ',': 0, 'A': 0,\
                '@': 0, 'E': 0, 'D': 0, 'G': 0, 'M': 0, 'L': 0, \
                'O': 0, 'N': 2, 'P': 0, 'S': 0, 'R': 0, 'U': 0,\
                 'T': 0, 'V': 1, 'Y': 0, 'X': 0, 'Z': 0, '^': 0, '~': 0}
def test_pos_features_counts():
    '''Test to confirm correct POS counts extracted for provided triples'''    
    #test1 - POS counts/single doc
    d = transformers.POScountExtractor()
    featureDict = d.transform(listOfTriples5)
    assert_equal(featureDict[0],posCountsTriples5)     
    #test2 - POS counts/multi doc
    d = transformers.POScountExtractor()
    featureDict = d.transform([listOfTriples5[0],listOfTriples5[0]])
    assert_equal(featureDict[0],posCountsTriples5)
    assert_equal(featureDict[1],posCountsTriples5)
    
#negation counts
negateTriples1 = [[["No_NEG","D",0.823],["one_NEG","N",0.5694],["enjoys_NEG","V",0.9992],["it_NEG","O",0.9884],[".",",",0.9991],["Ha","!",0.9701]]]
negateTriples2 = [[["I","O",0.9943],["wouldn't_NEG","V",0.9993],["do_NEG","V",1.0],["it_NEG","O",0.9895],[".",",",0.9993],["Never_NEG","!",0.826]]]
negateExpect1 ={'negation_count':1} 
negateExpect2 ={'negation_count':2} 
def test_negated_segment_counts():
    '''Test to confirm correct counts of negated segments returned'''    
    #test1 - negated segment counts/single doc - no segments
    d = transformers.negatedSegmentCountExtractor()
    featureDict = d.transform(listOfTriples2)
    assert_equal(featureDict[0],{'negation_count':0})     
    #test2 - negated segment counts/single doc - 1 segments
    d = transformers.negatedSegmentCountExtractor()
    featureDict = d.transform(negateTriples1)
    assert_equal(featureDict[0],negateExpect1)   
    #test3 - negated segment counts/single doc - 2 segments
    d = transformers.negatedSegmentCountExtractor()
    featureDict = d.transform(negateTriples2)
    assert_equal(featureDict[0],negateExpect2)      
 
    
    
#token counts
def test_token_counts():
    '''Test to confirm correct counts of tokens for each tweet'''    
    #test1 - token counts
    d = transformers.TokenCountExtractor()
    featureDict = d.transform(listOfTriples2)
    assert_equal(featureDict[0],{'token_count':2})  
    
    
    
#cluster
#"i": "0000"
#"tableau": "1111010101011"
#"hell": "010101100",
#"no": "1111111110",
#"88888": None
clusterTriples1 = [[["Hell","D",0.823],["no","N",0.5694],["88888","d",0.5694]]]
clusterTriples2 = [[["I","D",0.823],["Tableau","N",0.5694]]]

def test_docs_extractor():
    '''Test to confirm list of normalised docs are returned provided triples containing tokens'''
    d = transformers.ClusterExtractor()
    #no docs test
    assert_equal(d.transform([]),[])
    #single doc test - ensure case when none returned that nothing is attached at end of string
    assert_equal(d.transform(clusterTriples1),['010101100 1111111110'])
    #single doc test
    assert_equal(d.transform(clusterTriples2),['0000 1111010101011'])  

  
#KLUE AFINN polarity 
#    "abandon": -2.0,
#    "fear": -2.0, 
#    "aboard": 1.0, 
afinnTriples1 = [[["aboard","D",0.823],["ABANDON_NEG","N",0.5694],["fear","d",0.5694]]]
afinnTriples2 = [[["I","D",0.823],["Tableau","N",0.5694]]]
afinnPolarity1 = {'total_count_pos':1,
                 'total_count_neg':2,
                 'total_count_polar':3,
                 'mean_polarity':-1.0}
afinnPolarity2 = {'total_count_pos':0,
                 'total_count_neg':0,
                 'total_count_polar':0.0,
                 'mean_polarity':0.0}
#KLUE emoticon/acronym polarity 
#    ")x": -1.0,
#    "*alol*": 1.0,      
acroemotiTriples1 = [[[")x","E",0.823],["*alol*","N",0.5694]]]
acroemotiPolarity1 = {'total_count_pos':1,
                 'total_count_neg':1,
                 'total_count_polar':2,
                 'mean_polarity':0.0}
def test_klue_polarity_features_extractor():
    '''test to confirm KLUE afinn lexicon features are correctly extracted from triples'''
    d = transformers.KLUEpolarityExtractor()
    #test1 - multiple items in dict
    featureDict = d.transform(afinnTriples1)
    assert_equal(featureDict[0],afinnPolarity1)
    #test2 - no items in dict
    featureDict = d.transform(afinnTriples2)
    assert_equal(featureDict[0],afinnPolarity2)
    #test2 - no items in dict
    d = transformers.KLUEpolarityExtractor(lexicon='klue-both')
    featureDict = d.transform(acroemotiTriples1)
    assert_equal(featureDict[0],acroemotiPolarity1)
    
#GU-MLT SentiWordNet
#    "approximation+": 0.125,
#    "approximation-": 0.125,
gumltTriples1 = [[["my","D",0.823],["approximation","N",0.5694]]]
gumltTriples2 = [[["I","D",0.823],["Will","N",0.5694]]]
gumltTriples3 = [[["myy","D",0.823],["appproximation","N",0.5694]]]
gumltPolarity1 = {'sum_pos':0.125,
                 'sum_neg':0.125}
gumltPolarity2 = {'sum_pos':0.0,
                 'sum_neg':0.0}
gumltPolarity3 = {'sum_pos':0.125,
                 'sum_neg':0.125}                 
def test_gumlt_sentiwordnet_polarity_features_extractor():
    '''test to confirm GUMLT sentiwordnet lexicon features are correctly extracted from triples'''
    d = transformers.GUMLTsentiWordNetExtractor()
    #test1 - both neg and pos
    featureDict = d.transform(gumltTriples1)
    assert_equal(featureDict[0],gumltPolarity1)
    #test2 - score is 0
    featureDict = d.transform(gumltTriples2)
    assert_equal(featureDict[0],gumltPolarity2)    
    #test3 - both neg and pos with collapsed word
    featureDict = d.transform(gumltTriples1)
    assert_equal(featureDict[0],gumltPolarity1)
