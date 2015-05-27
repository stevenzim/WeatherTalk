'''
ml.py

Model module. The module allows you to create, evaluate and save models 
based on the specified classifier that is provided.  It is also necessary
to pass in a feature set and predictand set in numpy format
'''


import numpy as np
import pickle
from sklearn import cross_validation
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.externals import joblib

class MLmodel(object):
    '''
    Machine learning model class.  Takes in an arbitrary sklearn classifier
    along with feature set and predictand set to produce model binary files
    and evaluation metrics
    '''
    def __init__(self, ml_algorithm,X_set,Y_set):
        #input variables
        self.ml_algorithm = ml_algorithm    #initial sklearn classifier
        self.X_set = X_set                  #feature set numpy array
        self.Y_set = Y_set                  #predictand set numpy array
      
        #evaluations variables
        self.evalResult = None      #evaluation results e.g. Precision/recall
        self.cv_accuracy = None     #cross validation accuracy metrics
        self.confusionMatrix = None #confusion matrix metrics

        #model output variables
        self.model = ml_algorithm   #model binaries
        self.modelFileName = None   #output file name (should be full path)


    def saveModel(self, filename):
        '''Save model as binary files, these files will be necessary
        for future predictions on unseen data'''
        joblib.dump(self.model,filename)


    def crossValidate(self):
         '''Get cross-validation statitics for model
         10-Fold Cross Validation is used'''
         self.cv_accuracy = cross_validation.cross_val_score(\
         self.ml_algorithm, self.X_set, self.Y_set, cv=10)
         

    
    def evaluationResult(self,y_pred, Y_valid = None):
        '''Get evaluation results e.g. Precision, Recall and F1 scores'''
        if Y_valid != None:
	        self.Y_set = Y_valid
        self.evalResult = classification_report(self.Y_set,y_pred)
        self.confusionMatrix = confusion_matrix(self.Y_set,y_pred)
        
    def fitModel(self):
        '''Given ml_algorithm, build model with X's and Y's and store model'''
        classifier = self.ml_algorithm
        classifier.fit(self.X_set , self.Y_set)
        self.model = classifier
       
  
