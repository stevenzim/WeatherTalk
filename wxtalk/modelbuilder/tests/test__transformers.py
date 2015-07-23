from nose.tools import *
from wxtalk.modelbuilder import transformers
from wxtalk import helper

testRawTweet1 = "Your Not happy :( @user"
testTriple1 = [{"tagged_tweet_triples":[['Your', 'L', 0.7166], ['Not', 'R', 0.9968], ['happy', 'A', 0.9872], [':(', 'E', 0.955], ['@user', '@', 0.9974]],\
                "text":testRawTweet1}]
testExpected1 = [{'nlp_triples' : testTriple1[0]["tagged_tweet_triples"],\
                'raw_string' : testRawTweet1,\
                'raw_token_list' : ['Your', 'Not', 'happy', ':(', '@user'],\
                'pos_token_list' : ['L', 'R', 'A', 'E', '@'],\
                'normalised_token_list' : ['your', 'not', 'happy', ':('],\
                'normalised_string' : 'your not happy :(',\
                'stem_list' : ['your', 'not', 'happi', ':('],\
                'stem_string' : 'your not happi :(',\
                'negated_token_list' : ['your', 'not_NEG', 'happy_NEG', ':(_NEG'],\
                'negated_string' : 'your not_NEG happy_NEG :(_NEG',\
                'collapsed_token_list' : ['your', 'not', 'happy', ':('],\
                'negation_count' : 1,\
                'stanford_token_list' : None,\
                'stanford_pos_list' : None}]
                

                
testRawTweet2 = "I am happpppppyyyyyy"
testTriple2 = [{"tagged_tweet_triples":[['I', 'L', 0.7166], ['am', 'R', 0.9968], ['happpppppyyyyyy', 'A', 0.9872]],\
                "text":testRawTweet2}]   
testExpected2 = [{'nlp_triples' : testTriple2[0]["tagged_tweet_triples"],\
                'raw_string' : testRawTweet2,\
                'raw_token_list' : ['I', 'am', 'happpppppyyyyyy'],\
                'pos_token_list' : ['L', 'R', 'A'],\
                'normalised_token_list' : ['i', 'am', 'happpppppyyyyyy'],\
                'normalised_string' : "i am happpppppyyyyyy",\
                'stem_list' : ['i', 'am', 'happpppppyyyyyy'],\
                'stem_string' : "i am happpppppyyyyyy",\
                'negated_token_list' : ['i', 'am', 'happpppppyyyyyy'],\
                'negated_string' : "i am happpppppyyyyyy",\
                'collapsed_token_list' : ['i', 'am', 'happyy'],\
                'negation_count' : 0,\
                'stanford_token_list' : None,\
                'stanford_pos_list' : None}]

testRawTweet3 = "Your Not happy :( @user"
testTriple3 = [{"tagged_tweet_triples":[['Your', 'L', 0.7166], ['Not', 'R', 0.9968], ['happy', 'A', 0.9872], [':(', 'E', 0.955], ['@user', '@', 0.9974]],\
                "text":testRawTweet3}]  
testExpected3 = [{'nlp_triples' : testTriple3[0]["tagged_tweet_triples"],\
                'raw_string' : testRawTweet3,\
                'raw_token_list' : ['Your', 'Not', 'happy', ':(', '@user'],\
                'pos_token_list' : ['L', 'R', 'A', 'E', '@'],\
                'normalised_token_list' : ['your', 'not', 'happy', ':(','user'],\
                'normalised_string' : 'your not happy :( user',\
                'stem_list' : ['your', 'not', 'happi', ':(','user'],\
                'stem_string' : 'your not happi :( user',\
                'negated_token_list' : ['your', 'not_NEG', 'happy_NEG', ':(_NEG','user_NEG'],\
                'negated_string' : 'your not_NEG happy_NEG :(_NEG user_NEG',\
                'collapsed_token_list' : ['your', 'not', 'happy', ':(','user'],\
                'negation_count' : 1,\
                'stanford_token_list' : None,\
                'stanford_pos_list' : None}]


def test_tweet_transformer():
    '''Test to ensure tweet representation is properly built and returned'''
    #test 1 - everything + no user / no url in return
    t = transformers.TweetTransformer(userNorm = None,urlNorm = None)
    assert_equal(t.transform(testTriple1),testExpected1)
    #test 2 - everything + collapsing
    t = transformers.TweetTransformer(userNorm = '',urlNorm = '')
    assert_equal(t.transform(testTriple2),testExpected2)
    #test 3 - everything + url/user normalised to USER/URL(note, same functionality so only testing user switch
    t = transformers.TweetTransformer(userNorm = 'USER',urlNorm = 'URL')
    assert_equal(t.transform(testTriple3),testExpected3)

def test_transformed_tweet_vals_extractor():
    '''Test to ensure transformed tweet vals are correctly pulled from transformed tweet'''
    #test 1 - default negated
    t = transformers.DocsExtractor()
    assert_equal(t.transform(testExpected3),['your not_NEG happy_NEG :(_NEG user_NEG'])
    #test 1 - other field
    t = transformers.DocsExtractor('normalised_string')
    assert_equal(t.transform(testExpected3),['your not happy :( user'])
    #test 3 - default multiDoc
    t = transformers.DocsExtractor()
    assert_equal(t.transform([testExpected1[0],testExpected3[0]]),['your not_NEG happy_NEG :(_NEG','your not_NEG happy_NEG :(_NEG user_NEG'])
#----------------------lexicon tests

transformedTweets1 = [{'negated_token_list':['adore','him','back']}]
transformedTweets2 = [{'negated_token_list':['#hello','world']}]
#-------------manual lexicons
##bing and liu / transformedTweets1
##    "adore": 1.0,
bingLiuFeatures ={'total_count_pos':1,
                 'total_score_pos':1.0,
                 'max_score_pos':1.0,
                 'score_last_pos':1.0,
                 'total_count_neg':0,
                 'total_score_neg':0.0,
                 'min_score_neg':0.0,
                 'score_last_neg':0.0}
##MPQA / transformedTweets1
##    "adore": 1.0,
##    "back": 1.0,
mpqaFeatures ={'total_count_pos':2,
                 'total_score_pos':6.0,
                 'max_score_pos':5.0,
                 'score_last_pos':1.0,
                 'total_count_neg':0,
                 'total_score_neg':0.0,
                 'min_score_neg':0.0,
                 'score_last_neg':0.0}
#                     
##NRC emotions / transformedTweets1
##    "adore": 1.0,
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
    featureDict = d.transform(transformedTweets1)
    assert_equal(featureDict[0],bingLiuFeatures) 
    #test2 - single doc/MPQA
    d = transformers.NRCLexiconsExtractor(lexicon = 'MPQA')
    featureDict = d.transform(transformedTweets1)
    assert_equal(featureDict[0],mpqaFeatures) 
    #test3 - single doc/NRCemotions
    d = transformers.NRCLexiconsExtractor(lexicon = 'NRCemotion')
    featureDict = d.transform(transformedTweets1)
    assert_equal(featureDict[0],nrcEmotionFeatures) 



#--------automatic lexicons
##NRC140lexi / transformedTweets2
##    "world": "0.551",
nrc140FeaturesUnigrams = {'total_count_pos':1,
                 'total_score_pos':.551,
                 'max_score_pos':.551,
                 'score_last_pos':.551,
                 'total_count_neg':0,
                 'total_score_neg':0.0,
                 'min_score_neg':0.0,
                 'score_last_neg':0.0}


#                     
##NRC140lexi bigrams / transformedTweets1
##    "adore him": "1.435",
##    "him back": "-0.566",
nrc140FeaturesBigrams = {'total_count_pos':1,
                 'total_score_pos':1.435,
                 'max_score_pos':1.435,
                 'score_last_pos':1.435,
                 'total_count_neg':1,
                 'total_score_neg':-0.566,
                 'min_score_neg':-0.566,
                 'score_last_neg':-0.566}


def test_nrc_140_lexicon_features_extractor():
    '''test to confirm NRC 140 lexicon features are correctly extracted from triples'''
    #test1 - unigrams/single doc/NRC140
    d = transformers.NRCLexiconsExtractor(lexicon = 'NRC140',gramType = 'unigram',tagType = 'token')
    featureDict = d.transform(transformedTweets2)
    assert_equal(featureDict[0],nrc140FeaturesUnigrams) 
    #test2 - bigrams/single doc/NRC140
    d = transformers.NRCLexiconsExtractor(lexicon = 'NRC140',gramType = 'bigram',tagType = 'token')
    featureDict = d.transform(transformedTweets1)
    assert_equal(featureDict[0],nrc140FeaturesBigrams) 
#                                                   

##nrc hash lexicon / transformedTweets1
##    "#hello": "2.018",
##    "world": "0.384",
nrcHashFeaturesUnigrams = {'total_count_pos':2,
                 'total_score_pos':2.402,
                 'max_score_pos':2.018,
                 'score_last_pos':0.384,
                 'total_count_neg':0,
                 'total_score_neg':0.0,
                 'min_score_neg':0.0,
                 'score_last_neg':0.0}

def test_nrc_hash_lexicon_features_extractor():
    '''test to confirm NRC 140 lexicon features are correctly extracted from triples'''
    d = transformers.NRCLexiconsExtractor(lexicon = 'NRCHash',gramType = 'unigram',tagType = 'token')
    featureDict = d.transform(transformedTweets2)
    #test1 - unigrams/single doc/NRCHash
    assert_equal(featureDict[0],nrcHashFeaturesUnigrams)


#-----------POS count tests
transformedTweetsPOS1 = [{'pos_token_list':['V','N','N']}]
posCountsTweets1 = {'!': 0, '#': 0, '$': 0, '&': 0, ',': 0, 'A': 0,\
                '@': 0, 'E': 0, 'D': 0, 'G': 0, 'M': 0, 'L': 0, \
                'O': 0, 'N': 2, 'P': 0, 'S': 0, 'R': 0, 'U': 0,\
                 'T': 0, 'V': 1, 'Y': 0, 'X': 0, 'Z': 0, '^': 0, '~': 0}
def test_pos_features_counts():
    '''Test to confirm correct POS counts extracted for provided triples'''    
    #test1 - POS counts/single doc
    d = transformers.POScountExtractor()
    featureDict = d.transform(transformedTweetsPOS1)
    assert_equal(featureDict[0],posCountsTweets1)     
    #test2 - POS counts/multi doc
    d = transformers.POScountExtractor()
    featureDict = d.transform([transformedTweetsPOS1[0],transformedTweetsPOS1[0]])
    assert_equal(featureDict[0],posCountsTweets1)
    assert_equal(featureDict[1],posCountsTweets1)
    
    
#------------negation counts
def test_negated_segment_counts():
    '''Test to confirm correct counts of negated segments returned'''    
    #test1 - negated segment counts/single doc
    d = transformers.NegationCountExtractor()
    featureDict = d.transform(testExpected1)
    assert_equal(featureDict[0],{'negation_count':1})     
    #test2 - negated segment counts/multi doc - 1 segments
    d = transformers.NegationCountExtractor()
    featureDict = d.transform([testExpected1[0],testExpected2[0]])
    assert_equal(featureDict[0],{'negation_count':1})   
    assert_equal(featureDict[1],{'negation_count':0})   
    
#------------encodings
capsTweets1 = [{'raw_token_list' : ['#Hello', 'Woorrlld']}]
capsTweets2 = [{'raw_token_list' : ['ADORE', '#him','#BACK']}]
def test_caps_counts():
    '''Test to confirm correct counts of Capitilized words is returned'''    
    #test1 - Caps counts/single doc
    d = transformers.CapsCountExtractor()
    featureDict = d.transform(capsTweets1)
    assert_equal(featureDict[0],{'total_count_caps':0})     
    #test2 - Caps counts/single doc
    d = transformers.CapsCountExtractor()
    featureDict = d.transform(capsTweets2)
    assert_equal(featureDict[0],{'total_count_caps':2})  

hashTweets1 = [{'pos_token_list' : ['#', 'N']}]
hashTweets2 = [{'pos_token_list' : ['V', '#','#']}]
def test_hashtag_counts():
    '''Test to confirm correct counts of hashtags is returned'''    
    #test1 - hashtags counts/single doc
    d = transformers.HashCountExtractor()
    featureDict = d.transform(hashTweets1)
    assert_equal(featureDict[0],{'total_count_hash':1})     
    #test2 - hashtags counts/single doc
    d = transformers.HashCountExtractor()
    featureDict = d.transform(hashTweets2)
    assert_equal(featureDict[0],{'total_count_hash':2}) 
    
elongatedTweets1 = [{'normalised_token_list' : ["hello","worlld"]}]
elongatedTweets2 = [{'normalised_token_list' : ["hellooo","#wooorld","yyyyes","!!!!"]}]
def test_elongated_word_counts():
    '''Test to confirm correct counts of elongated words returned'''    
    #test1 - elongated words counts/single doc
    d = transformers.ElongWordCountExtractor()
    featureDict = d.transform(elongatedTweets1)
    assert_equal(featureDict[0],{'total_count_elong':0} )     
    #test2 - elongated words counts/single doc
    d = transformers.ElongWordCountExtractor()
    featureDict = d.transform(elongatedTweets2)
    assert_equal(featureDict[0],{'total_count_elong':3} )  
    
##Punctuation
punctuationTweets1 = [{'normalised_token_list' : ["hello","worlld","!"]}]
punctuationTweets2 = [{'normalised_token_list' : ["hello","???","worlld","!!!","me","!?!?!?"]}]
punctuationTweets3 = [{'normalised_token_list' : ["hello","!!!","worlld","!!!","me","???"]}]
punct1 = {'count_contig_seq_exclaim':0,
            'count_contig_seq_question':0,
            'count_contig_seq_both':0,
            'last_toke_contain_quest':False,
            'last_toke_contain_exclaim':True}
punct2 = {'count_contig_seq_exclaim':1,
            'count_contig_seq_question':1,
            'count_contig_seq_both':1,
            'last_toke_contain_quest':True,
            'last_toke_contain_exclaim':True}            
punct3 = {'count_contig_seq_exclaim':2,
            'count_contig_seq_question':1,
            'count_contig_seq_both':0,
            'last_toke_contain_quest':True,
            'last_toke_contain_exclaim':False}  
def test_punctuation_features():
    '''Test to confirm correct features returned for punctuation'''    
    #test1 - punctuation feastures/single doc
    d = transformers.PunctuationFeatureExtractor()
    featureDict = d.transform(punctuationTweets1)
    assert_equal(featureDict[0],punct1)     
    #test2 - punctuation feastures/single doc
    d = transformers.PunctuationFeatureExtractor()
    featureDict = d.transform(punctuationTweets2)
    assert_equal(featureDict[0],punct2)                
    #test3 - punctuation feastures/single doc
    d = transformers.PunctuationFeatureExtractor()
    featureDict = d.transform(punctuationTweets3)
    assert_equal(featureDict[0],punct3)   
    
#emoticons
emoticonTweets1 = [{'raw_token_list' : ['#Hello', 'Woorrlld']}]
emoticonTweets2 = [{'raw_token_list' : [':-)', '#him',':-(']}]
emoticonTrip1 ={'positive_emoticon_present':False,
                'negative_emoticon_present':False,
                'last_emoticon_pos':False,
                'last_emoticon_neg':False} 
emoticonTrip2 ={'positive_emoticon_present':True,
                'negative_emoticon_present':True,
                'last_emoticon_pos':False,
                'last_emoticon_neg':True} 

def test_emoticons_lexicon_features():
    '''Test to confirm correct vals returned for emoticon features'''    
    #test1 - No emoticons/single doc
    d = transformers.EmoticonExtractor(lexicon = 'emoticon')
    featureDict = d.transform(emoticonTweets1)
    assert_equal(featureDict[0],emoticonTrip1)     
    #test2 - Several emoticons/single doc
    d = transformers.EmoticonExtractor(lexicon = 'emoticon')
    featureDict = d.transform(emoticonTweets2)
    assert_equal(featureDict[0],emoticonTrip2)  

#clusters
#"i": "0000"
#"tableau": "1111010101011"
#"hell": "010101100",
#"no": "1111111110",
#"88888": None
clusterTweet1  = [{'normalised_token_list' :["hell","no","88888"]}]
clusterTweet2  = [{'normalised_token_list' :["i","tableau"]}]
def test_clusters_extractor():
    '''Test to confirm concatenated cluster id strings are returned provided transformed tweets'''
    d = transformers.ClusterExtractor()
    #no docs test
    assert_equal(d.transform([]),[])
    #single doc test - ensure case when none returned that nothing is attached at end of string
    assert_equal(d.transform(clusterTweet1),['010101100 1111111110'])
    #single doc test
    assert_equal(d.transform(clusterTweet2),['0000 1111010101011'])
    #multi doc test
    assert_equal(d.transform([clusterTweet1[0],clusterTweet2[0]]),['010101100 1111111110','0000 1111010101011'])
    

    
#-----------KLUE features
#token counts
normalisedTweets1 = [{'normalised_token_list' : ["hello","worlld","!"]}]
def test_token_counts():
    '''Test to confirm correct counts of tokens for each tweet'''    
    #test1 - token counts
    d = transformers.TokenCountExtractor()
    featureDict = d.transform(normalisedTweets1)
    assert_equal(featureDict[0],{'token_count':3})  

#KLUE AFINN polarity 
#    "abandon": -2.0,
#    "fear": -2.0, 
#    "aboard": 1.0, 
afinnTweet1 = [{"stem_list":["aboard","abandon","fear"]}]
afinnTweet2 = [{"normalised_token_list":["i","tableau"]}]
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
acroemotiTweet1 = [{"normalised_token_list":[")x","*alol*"]}]
acroemotiPolarity1 = {'total_count_pos':1,
                 'total_count_neg':1,
                 'total_count_polar':2,
                 'mean_polarity':0.0}
def test_klue_polarity_features_extractor():
    '''test to confirm KLUE afinn lexicon features are correctly extracted from triples'''
    d = transformers.KLUEpolarityExtractor()
    #test1 - multiple items in dict
    featureDict = d.transform(afinnTweet1)
    assert_equal(featureDict[0],afinnPolarity1)
    #test2 - no items in dict
    d = transformers.KLUEpolarityExtractor(tokenListKeyName="normalised_token_list" )
    featureDict = d.transform(afinnTweet2)
    assert_equal(featureDict[0],afinnPolarity2)
    #test2 - no items in dict
    d = transformers.KLUEpolarityExtractor('klue-both',"normalised_token_list" )
    featureDict = d.transform(acroemotiTweet1)
    assert_equal(featureDict[0],acroemotiPolarity1)
    
#-----------GU-MLT SentiWordNet lexicon features
#    "approximation+": 0.125,
#    "approximation-": 0.125,
gumltTweet1 = [{"negated_token_list":["my","approximation"]}]
gumltTweet2 = [{"negated_token_list":["i","will"]}]
gumltTweet3 = [{"collapsed_token_list":["myy","approximation"]}]
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
    featureDict = d.transform(gumltTweet1)
    assert_equal(featureDict[0],gumltPolarity1)
    #test2 - score is 0
    featureDict = d.transform(gumltTweet2)
    assert_equal(featureDict[0],gumltPolarity2)    
    #test3 - both neg and pos with collapsed word
    d = transformers.GUMLTsentiWordNetExtractor(tokenListKeyName= "collapsed_token_list")
    featureDict = d.transform(gumltTweet3)
    assert_equal(featureDict[0],gumltPolarity3)
