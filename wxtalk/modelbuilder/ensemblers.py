'''Module to compile ensemble predictions on tweets for sentiment classification and 
weather topic classification.   
input 1: list containing ensemble parameter dicts (which includes underlying model ids
input 2: list of tweet dictionarys containing individual model predictions
returns: Original dicts + ensemble results
Key steps
1 - Load tweets
2 - For each ensemble param dict and each tweet
    a - calculated sum of probabilistic predictions for each class of each model
    b - take the mean of each class by the total number of model ids in the ensemble params dictionary
    c - add key values for discrete class (which is index of mean in 2b which is maximum)
    d - add key values for probability of winning class (which is value of 2b which is maximum)
3 - return the updated list of dict
 '''
 
#example to update dicts in list
#l = [{'key1':1}]
#for i in enumerate(l):
#    n = i[0]
#    d = i[1]
#    d['key2'] =3
#    l[n] = d
 

from wxtalk.modelbuilder import transformers
from wxtalk import helper


                    

def compileEnsemble(listOfEnsembleMetaDicts,listOfTweetDicts):
    return None
