'''Module to make predictions on tweets for sentiment classification and 
weather topic classification.   
input 1: list containing model parameter dicts
input 2: file containing tweets
input 3: output file for predicted tweets
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
5 - Dump to output file'''

from wxtalk.model import transformers
from wxtalk import helper


                    
NRCmodelMetaData = {"binary_folder_file":"/sentiment/NRC/model.pkl",\
                "classifier_type":"sentiment",\
                "description":"Implementation of NRC 2013 Semeval features trained with logistic regression",\
                "id":"s1",\
                "name":"NRC-2013",\
                "normalisation_params":{"userNorm" : None,\
                                        "urlNorm" : None,\
                                        "hashNormalise":False,\
                                        "digitNormalise":False}}
                                        
KLUEmodelMetaData = {"binary_folder_file":"/sentiment/KLUE/model.pkl",\
                "classifier_type":"sentiment",\
                "description":"Implementation of KLUE 2013 Semeval features trained with logistic regression",\
                "id":"s2",\
                "name":"KLUE-2013",\
                "normalisation_params":{"userNorm" : None,\
                                        "urlNorm" : None,\
                                        "hashNormalise":True,\
                                        "digitNormalise":False}}

GUMLTLTmodelMetaData = {"binary_folder_file":"/sentiment/GUMLT/model.pkl",\
                "classifier_type":"sentiment",\
                "description":"Implementation of GU-MLT-LT 2013 Semeval features trained with logistic regression",\
                "id":"s3",\
                "name":"GU-MLT-LT-2013",\
                "normalisation_params":{"userNorm" : None,\
                                        "urlNorm" : None,\
                                        "hashNormalise":False,\
                                        "digitNormalise":False}}
                                        
TeamXMetaData = {"binary_folder_file":"/sentiment/TeamX-inspired/model.pkl",\
                "classifier_type":"sentiment",\
                "description":"Implementation of TeamX 2014 inspired Semeval features trained with logistic regression",\
                "id":"s4",\
                "name":"TeamX-2014",\
                "normalisation_params":{"userNorm" : None,\
                                        "urlNorm" : None,\
                                        "hashNormalise":True,\
                                        "digitNormalise":False}}
def makePredictions(listOfModelMetaDicts,listOfTweetDicts):
    return None
