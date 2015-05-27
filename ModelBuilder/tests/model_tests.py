from nose.tools import *
import raop.model.ml as model
from sklearn import datasets
from sklearn import svm
from sklearn.externals import joblib
import numpy as np

iris_testdata = datasets.load_iris()
X_set, Y_set = iris_testdata.data, iris_testdata.target
classifier = svm.SVC()
outputModelFileName = 'test-data/pickle-items/test-output.pkl'
inputModelFileName = 'test-data/pickle-items/test-input.pkl'

def test_save_model():
    modelObj = model.MLmodel(classifier,X_set, Y_set)
    modelObj.saveModel(outputModelFileName)
    origModel = joblib.load(inputModelFileName)
    newModel = joblib.load(outputModelFileName)
    #this test shows that attributes matchs from the two model objects
    assert_equal(origModel.kernel,newModel.kernel)

def crossValidate_test():
    expected_results = [ 1.,  1., 0.86666666666666667,1.,  0.93333333333333335,\
    1.,1.,  1., 1.,  1. ]
    modelObj = model.MLmodel(classifier,X_set, Y_set)
    modelObj.crossValidate()
    assert_equal((expected_results == modelObj.cv_accuracy).all(), True)
 
def eval_test():
    evalOutput = '             precision    recall  f1-score   support\n\n      False       0.67      1.00      0.80         2\n       True       1.00      0.50      0.67         2\n\navg / total       0.83      0.75      0.73         4\n'	
    expectedConfMatrix = np.array([[2,0],[1,1]])
    y_true = [True,True,False,False]
    y_pred = [True,False,False,False]
    modelObj = model.MLmodel(None,None,y_true)
    modelObj.evaluationResult(y_pred)

    assert_equal(modelObj.evalResult, evalOutput)
    assert_equal((modelObj.confusionMatrix==expectedConfMatrix).all(),True)
    
#TODO: Need test for fitModel function

