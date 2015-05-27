from nose.tools import *
import raop.helper as helper

inFileName = "test-data/oneJSONentry.json"
outFileName = "test-data/outputOneJSONentry.json"

def test_JSON_load_unload():
	'''Test to load json data and verify that unloaded data is still the same as original data'''
	initialData = helper.loadJSONfromFile(inFileName)
	helper.dumpJSONtoFile(outFileName, initialData)
	dumpedData = helper.loadJSONfromFile(outFileName)
	assert_equal(initialData,dumpedData)
