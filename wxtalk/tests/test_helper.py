from nose.tools import *
import wxtalk.helper as helper

inFileName = "test-data/oneJSONentry.json"
outFileName = "test-data/outputOneJSONentry.json"

def test_JSON_load_unload():
	'''Test to load json data and verify that unloaded data is still the same as original data'''
	initialData = helper.loadJSONfromFile(inFileName)
	helper.dumpJSONtoFile(outFileName, initialData)
	dumpedData = helper.loadJSONfromFile(outFileName)
	assert_equal(initialData,dumpedData)
	
def test_drop_keys_vals_listOfDicts():
    '''Tests to verify keys and vals are dropped correctly from list of dicts'''
    listOfDicts = [{'test': 5, 'length': 5}, {'test': 2, 'length': 2}]
    helper.dropKeysVals(listOfDicts, keysToDrop = [])
    assert_equal(helper.dropKeysVals(listOfDicts, keysToDrop = []),listOfDicts) #test none-dropped
    assert_equal(helper.dropKeysVals(listOfDicts, ['test']),\
    [{'length': 5}, {'length': 2}]) #test one-dropped
    assert_equal(helper.dropKeysVals([{'test': 5, 'length': 5}, {'test': 2, 'length': 2}]\
    , ['test','length']),\
    [{}, {}]) #test both-dropped
    assert_raises(TypeError,\
                helper.dropKeysVals,listOfDicts, 'test' ) #test error thrown when list not passed
    assert_raises(ValueError,\
                helper.dropKeysVals,listOfDicts, ['txt'] ) #test error thrown when wrong keyname passed


#test files for tweetNLP                
tweetNLPactualOutFileName = "test-data/postTweetNLP-temp.json"
tweetNLPinFileName = "test-data/preTweetNLP-test.json"
tweetNLPexpectedOutFileName = "test-data/postTweetNLP-test.json"

semEvalTemp = "test-data/SemEval/SemEvalTemp.json"
semEvalRawFile = "test-data/SemEval/1-SemEvalRaw.json"
semEvalTriplesFile = "test-data/SemEval/2-SemEvalTriples.json"

liveTweetsTemp = "test-data/LiveTweets/LiveTweetsTemp.json"
liveTweetsRawFile = "test-data/LiveTweets/1-LiveTweetsRaw.json"
liveTweetsTriplesFile = "test-data/LiveTweets/2-LiveTweetsTriples.json"

obamaListIn =     [{"text": "I am Obama?"},{"text": "I am #ObaMa?"},{"text": "I am Ted?"}]
obamaListOut =     [{"text": "I am Obama?","topic_obama":True},\
                    {"text": "I am #ObaMa?","topic_obama":True},\
                    {"text": "I am Ted?","topic_obama":False}]


def test_extract_tweetNLP():
	'''Test for tweetNLP extraction helper function. To add TweetNLP triples to list of dictionaries'''
	#basic test
	expectedOutput = helper.loadJSONfromFile(tweetNLPexpectedOutFileName)
	helper.extractTweetNLPtriples(tweetNLPinFileName,tweetNLPactualOutFileName)
	actualOutput = helper.loadJSONfromFile(tweetNLPactualOutFileName)
	assert_equal(expectedOutput,actualOutput)
	#test on semeval input format
	expectedOutput = helper.loadJSONfromFile(semEvalTriplesFile)
	helper.extractTweetNLPtriples(semEvalRawFile,semEvalTemp)
	actualOutput = helper.loadJSONfromFile(semEvalTemp)
	assert_equal(expectedOutput,actualOutput)
#	#test on live tweet input format
	expectedOutput = helper.loadJSONfromFile(liveTweetsTriplesFile)
	helper.extractTweetNLPtriples(liveTweetsRawFile,liveTweetsTemp)
	actualOutput = helper.loadJSONfromFile(liveTweetsTemp)
	assert_equal(expectedOutput,actualOutput)
	
def test_add_simple_topic():
    results = helper.addStringTestTopic(dictionary = obamaListIn[0],keyToSearch = 'text',stringToTest = "obama",keyNameToAdd = "topic_obama")
    assert_equal(results,obamaListOut[0])
    results = helper.addStringTestTopic(dictionary = obamaListIn[1],keyToSearch = 'text',stringToTest = "oBama",keyNameToAdd = "topic_obama")
    assert_equal(results,obamaListOut[1])
    results = helper.addStringTestTopic(dictionary = obamaListIn[2],keyToSearch = 'text',stringToTest = "obama",keyNameToAdd = "topic_obama")
    assert_equal(results,obamaListOut[2])        
