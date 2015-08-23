'''Module to make predictions on tweets for sentiment classification and 
weather topic classification, each parameter dictionary contains location of model binary files.   
input 1: list containing model parameter dicts
input 2: list of tweet dicts
Key steps
1 - Load tweets
2 - Extract CMU NLP TRIPLES
3 - For each model param dict
    a - transform tweets per normalisation params
    b - load corresponding model binaries
    c - predict discrete class for model
    d - predict probabilities
    e - update tweets with model probs/discrete preds
4 - Pop all triples
5 - Return Scored tweets'''

from wxtalk.model import transformers as tran
from wxtalk import helper

import sklearn.externals.joblib as joblib

import random
import os

modelBinaryPath = helper.getProjectPath() + '/wxtalk/resources/models'
tempFilePath = helper.getProjectPath() + '/wxtalk/resources/temp'

def makePredictions(listOfModelMetaDicts,listOfTweetDicts):
    '''Provided model params and list of tweet dicts, returns tweet dicts with list of probabilistic results for each class and 
    discrete winning class for each model, see module doc string for more details'''
    print "Extracting Tweet Triples..."
    #get triples for list of tweets
    #The dump and reload to tempTriples file is a hack to deal with a unicode error in stemmer (see error string in transform function of transformers.TweetTransformer)
    tweetsWithTriplesB4 = helper.extractTweetNLPtriples(listOfTweetDicts)
    tempTripleFileName = tempFilePath + '/tempTriples-' +str(random.randint(1,10000000)) + '.json' #create temp file name with random number 0-->10x10^7 to minimize possible locks from multi threads
    helper.dumpJSONtoFile(tempTripleFileName,tweetsWithTriplesB4)  #dump triples to temp file
    tweetsWithTriples = helper.loadJSONfromFile(tempTripleFileName) #reload  temp file
    os.remove(tempTripleFileName) #delete temp file
    
    for model in listOfModelMetaDicts:
            print "Predicting results for model: " + model["name"]
            #initialise transformer and load model
            normPs = model["normalisation_params"]
            twitTrans = tran.TweetTransformer(normPs["userNorm"], normPs["urlNorm"],normPs["hashNormalise"],normPs["digitNormalise"])
            transformedTweets = twitTrans.transform(tweetsWithTriples) 
            predictor = joblib.load(modelBinaryPath + model["binary_path"])
            #get discrete and probabilistic predictions
            discrete_preds = predictor.predict(transformedTweets)
            probabilistic_preds = predictor.predict_proba(transformedTweets)
            #convert predictions from numpy arrays to list
            disc_preds_list = discrete_preds.tolist()
            proba_preds_list = probabilistic_preds.tolist()
            
            #append preds to tweetsWithTriples
            for dict in enumerate(tweetsWithTriples):
                idx = dict[0]
                tweet = dict[1]
                tweet[model["id"]+"_discrete"] = disc_preds_list[idx]
                tweet[model["id"]+"_proba"] = map(lambda pred: round(pred,3),proba_preds_list[idx]) #3 point precision
                tweetsWithTriples[idx] = tweet
    
    #drop triples from tweetsWithTriples and return list of tweets with model preds
    for tweet in enumerate(tweetsWithTriples):
        idx = tweet[0]
        keyValDropped = tweetsWithTriples[idx].pop("tagged_tweet_triples",None)  #stored as variable in order to supress print to screen
    return tweetsWithTriples

#SENTIMENT CLASSIFIERS
NRCmodelMetaData = {"binary_path":"/sentiment/NRC/model.pkl",\
                "classifier_type":"sentiment",\
                "description":"Implementation of NRC 2013 Semeval features trained with logistic regression",\
                "id":"s1",\
                "name":"NRC-2013",\
                "normalisation_params":{"userNorm" : None,\
                                        "urlNorm" : None,\
                                        "hashNormalise":False,\
                                        "digitNormalise":False}}
                                        
KLUEmodelMetaData = {"binary_path":"/sentiment/KLUE/model.pkl",\
                "classifier_type":"sentiment",\
                "description":"Implementation of KLUE 2013 Semeval features trained with logistic regression",\
                "id":"s2",\
                "name":"KLUE-2013",\
                "normalisation_params":{"userNorm" : None,\
                                        "urlNorm" : None,\
                                        "hashNormalise":False,\
                                        "digitNormalise":False}}

GUMLTLTmodelMetaData = {"binary_path":"/sentiment/GUMLT/model.pkl",\
                "classifier_type":"sentiment",\
                "description":"Implementation of GU-MLT-LT 2013 Semeval features trained with logistic regression",\
                "id":"s3",\
                "name":"GU-MLT-LT-2013",\
                "normalisation_params":{"userNorm" : None,\
                                        "urlNorm" : None,\
                                        "hashNormalise":False,\
                                        "digitNormalise":False}}
                                        
#WEATHER CLASSIFIERS
                                        
wxFullFeats = {"binary_path":"/topic-wx/all-feats/model.pkl",\
                "classifier_type":"weather-topic",\
                "description":"Custom built classifier(trained on all-features with logisitc regression), to determine if a tweet is/ is not about the weather",\
                "id":"w1",\
                "name":"wx-full-feats",\
                "normalisation_params":{"userNorm" : None,\
                                        "urlNorm" : None,\
                                        "hashNormalise":False,\
                                        "digitNormalise":False}}

wxUnigrams = {"binary_path":"/topic-wx/unigrams/model.pkl",\
                "classifier_type":"weather-topic",\
                "description":"Custom built classifier(trained on unigrams only with logisitc regression), to determine if a tweet is/ is not about the weather",\
                "id":"w2-unis",\
                "name":"wx-unigrams",\
                "normalisation_params":{"userNorm" : None,\
                                        "urlNorm" : None,\
                                        "hashNormalise":False,\
                                        "digitNormalise":False}}


