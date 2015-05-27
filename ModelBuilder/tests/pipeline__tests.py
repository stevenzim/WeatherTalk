from nose.tools import *
import raop.helper as helper
import raop.pipeline as pipeline
import os
import numpy as np

keysInFileName = "test-data/oneJSONentry.json"
keysOutFileName = "test-data/output-part1-keys-removed-oneJSONentry.json"
inFileName = "test-data/utf-encoding-test.json"
outFileName = "test-data/output-part2-utf-encoding-test.json"
outTestFileName = "test-data/output-part2-utf-encoding-test-testset.json"

def test_part1_remove_keys():
	'''Test for part 1 of pipeline. The keys listed in function must be removed'''
	expectedOutput = helper.loadJSONfromFile(keysOutFileName)
	pipeline.removeNonNeededKeys(keysInFileName,keysOutFileName)
	actualOutput = helper.loadJSONfromFile(keysOutFileName)
	assert_equal(expectedOutput,actualOutput)


def test_part2_withUTF():
	'''Test for part 2 of pipeline. The text string must be encoded and decoded 
	therefore this is tested too'''
	expectedOutput = helper.loadJSONfromFile(outFileName)
	pipeline.addPreprocessedKeyVals(inFileName,outFileName)
	actualOutput = helper.loadJSONfromFile(outFileName)
	assert_equal(expectedOutput,actualOutput)

def test_part3_getFeatures():
    '''Test for part 3 of pipeline. 
    Extract features from JSON file and Create a feature vectors for each instance'''
    expectedX=np.array([[0,616,294.1380208333333,0,3,5,4,4,0,233,0.0,1]])
    expectedY=np.array([False])
    actualX, actualY = pipeline.getFeatures(outFileName,0)
    assert_equal(expectedX.all(),actualX.all())
    assert_equal(expectedY.all(),actualY.all())
    actualX = pipeline.getFeatures(outFileName,1)
    assert_equal(expectedX.all(),actualX.all())
    
    
def test_part4_buildModel_and_results():
    '''Test to confirm that report is properly output.  The output report
    should match the expected report.  If results match then it is confirm that
    other pipeline components are working as well (e.g. saving model files)
    however other functionality is tested elsewhere'''
    path = os.path.dirname(os.getcwd())
    trainFile = path + '/resources/2-train-preprocessed-keys-added.json'
    modelOutpath = path + '/resources/models/'

    #fetch features and requestor results (i.e. X's and Y's)
    features, pizzas = pipeline.getFeatures(trainFile,0)

    #model details
    from sklearn.naive_bayes import GaussianNB
    classifier = GaussianNB()
    modelName = "GaussianNaiveBayes"
    directoryName = "GaussianNaiveBayes"
    description = "Steven Zimmerman - March 3rd 2015 - Gaussian Naive Bayes"

    pipeline.modelPipeline(classifier, features, pizzas, modelOutpath,\
    modelName, directoryName, description)
    
    fullReportPath = modelOutpath + directoryName + '/' + modelName + '.report'
    expectedReportPath = 'test-data/expected-GaussianNaiveBayes.report'
    
    testOutFile = open(fullReportPath,'r')
    testExpectedFile = open(expectedReportPath, 'r')
    outLines = []
    expectLines = []
    
    for line in testOutFile:
        outLines.append(line)
    for line in testExpectedFile:
        expectLines.append(line)
    assert_equal(outLines,expectLines)
 
