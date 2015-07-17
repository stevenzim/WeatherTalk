from nose.tools import *
from wxtalk.modelbuilder import transformers
from wxtalk import helper


listOfTriples1 = [[['#Hello','#',.9],['Woorrlld','N',.9]]]
listOfTriples2 = [[['ADORE','V',.9],['#him','#',.9],['#BACK','#',.9]]]
listOfTriples3 = [[["hello","!",0.985],["worlld","N",0.5999]]]
listOfTriples4 = [[["hellooo","!",0.9856],["#wooorld","N",0.7088],["yyyyes","!",0.9246],["!!!!",",",0.9918]]]
listOfTriples5 = [[["Hello","!",0.9755 ], ["World","N",0.4421 ], ["!",",",0.9991 ]]]
listOfTriples6 = [[["Hello","!",0.9964 ], ["???",",",0.9939 ], ["World","N",0.6539 ], ["!!!",",",0.9982 ], ["me","O",0.9964 ], ["!?!?!?",",",0.9888 ]]]
listOfTriples7 = [[["Hello","!",0.9964 ], ["!!!",",",0.9939 ], ["World","N",0.6539 ], ["!!!",",",0.9982 ], ["me","O",0.9964 ], ["???",",",0.9888 ]]]

####-----NRC encodings
# the number of words in all caps
capsTrip1 ={'total_count_caps':0}
capsTrip2 ={'total_count_caps':2}

def test_caps_counts():
    '''Test to confirm correct counts of Capitilized words is returned'''    
    #test1 - Caps counts/single doc
    d = transformers.capsCountExtractor()
    featureDict = d.transform(listOfTriples1)
    assert_equal(featureDict[0],capsTrip1)     
    #test2 - Caps counts/single doc
    d = transformers.capsCountExtractor()
    featureDict = d.transform(listOfTriples2)
    assert_equal(featureDict[0],capsTrip2)  

## the number of hashtags
#hashTrip1 ={'total_count_hash':1}
#hashTrip2 ={'total_count_hash':2}

#def test_hashtag_counts():
#    '''Test to confirm correct counts of hashtags is returned'''    
#    #test1 - hashtags counts/single doc
#    d = transformers.hashCountExtractor()
#    featureDict = d.transform(listOfTriples1)
#    assert_equal(featureDict[0],hashTrip1)     
#    #test2 - hashtags counts/single doc
#    d = transformers.hashCountExtractor()
#    featureDict = d.transform(listOfTriples2)
#    assert_equal(featureDict[0],hashTrip2)  

##elongated words
#elongTrip3 ={'total_count_elong':0} 
#elongTrip4 ={'total_count_elong':3} 
#def test_elongated_word_counts():
#    '''Test to confirm correct counts of elongated words returned'''    
#    #test1 - elongated words counts/single doc
#    d = transformers.elongWordCountExtractor()
#    featureDict = d.transform(listOfTriples3)
#    assert_equal(featureDict[0],elongTrip3)     
#    #test2 - elongated words counts/single doc
#    d = transformers.elongWordCountExtractor()
#    featureDict = d.transform(listOfTriples4)
#    assert_equal(featureDict[0],elongTrip4)  


##Punctuation
#puncTrip5 = {'count_contig_seq_excaim':0,
#            'count_contig_seq_question':0,
#            'count_contig_seq_both':0,
#            'last_toke_contain_quest':False,
#            'last_toke_contain_exclaim':True}
#puncTrip6 = {'count_contig_seq_exclaim':1,
#            'count_contig_seq_question':1,
#            'count_contig_seq_both':1,
#            'last_toke_contain_quest':True,
#            'last_toke_contain_exclaim':True}            
#puncTrip7 = {'count_contig_seq_exclaim':2,
#            'count_contig_seq_question':1,
#            'count_contig_seq_both':0,
#            'last_toke_contain_quest':True,
#            'last_toke_contain_exclaim':False}  
#def test_punctuation_features():
#    '''Test to confirm correct features returned for punctuation'''    
#    #test1 - punctuation feastures/single doc
#    d = transformers.punctuationFeatureExtractor()
#    featureDict = d.transform(listOfTriples5)
#    assert_equal(featureDict[0],puncTrip5)     
#    #test2 - punctuation feastures/single doc
#    d = transformers.punctuationFeatureExtractor()
#    featureDict = d.transform(listOfTriples6)
#    assert_equal(featureDict[0],puncTrip6)                
#    #test3 - punctuation feastures/single doc
#    d = transformers.punctuationFeatureExtractor()
#    featureDict = d.transform(listOfTriples7)
#    assert_equal(featureDict[0],puncTrip7)    



            

