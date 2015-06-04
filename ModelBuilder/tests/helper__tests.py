from nose.tools import *
import twxeety.helper as helper

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

