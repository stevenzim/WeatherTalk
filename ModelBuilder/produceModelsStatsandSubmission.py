import raop.pipeline as pipeline
import raop.model.ml as model
from sklearn.externals import joblib
import numpy as np
import raop.helper as helper
import os



def buildModels(classifier, modelName, directoryName, modelOutpath, description, additionalFeaturesList, trainFile, testFile):
    #fetch features and requestor results (i.e. X's and Y's), 
    #params = (file, train = 0 test = 1, additonal features to include)
    print 'Extracting Features....'
    features, pizzas = pipeline.getFeatures(trainFile,0,additionalFeaturesList)

    #normalize the feature set
    from sklearn import preprocessing
    scaler = preprocessing.StandardScaler().fit(features)
    features = scaler.transform(features)


    #PRODUCE MODEL and EVAL METRICS
    print 'Building Model and Evaluating Results....'
    pipeline.modelPipeline(classifier, features, pizzas, modelOutpath, modelName, directoryName, description)



    #PREPARE SUBMISSION FILE
    #path and filename info
    print 'Loading specificied model and extracting features on unseen data....'
    inputModelFileName = modelOutpath + directoryName + '/' + modelName
    model = joblib.load(inputModelFileName)

    #fetch features  (i.e. X's )
    #params = (file, train = 0 test = 1, additonal features to include)
    features = pipeline.getFeatures(testFile,1,additionalFeaturesList)
    listofID = []
    testdata = helper.loadJSONfromFile(testFile)
    for item in testdata:
        listofID.append(item["request_id"])
        
    #scale the features
    features = scaler.transform(features)


    #get results predcitions and convert to list
    print 'Model is making predictions...'		
    results = model.predict(features)
    results_list=results.tolist()


    #write results and user details to submission file
    outputFile=open(inputModelFileName + '-KaggleSubmission.csv','w')

    outputFile.write("request_id,requester_received_pizza\n")
    for counter,id in enumerate(listofID):
        outputFile.write(id+",")
        if results_list[counter]:
            outputFile.write('1\n')
        else:
            outputFile.write('0\n')

    outputFile.close()
    
    print 'File is ready for submission to Kaggle...'
