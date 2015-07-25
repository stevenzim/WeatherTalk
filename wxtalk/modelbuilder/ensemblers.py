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


from wxtalk.modelbuilder import transformers
from wxtalk import helper

import itertools

def compileEnsemble(listOfEnsembleMetaDicts,listOfTweets):
    '''Provided ensemble params and list of tweet dicts, returns tweet dicts with probabilistic results for winning class and 
    discrete value of winning class for each ensemble, see module doc string for more details'''
    listOfTweetDicts = listOfTweets
    for ensemble in listOfEnsembleMetaDicts:
        print "Predicting results for ensemble: " + ensemble["description"]
        modelIds = ensemble["model_id_list"]
        for dict in enumerate(listOfTweetDicts):
            idx = dict[0]
            tweet = dict[1]
            allModelProbas4Tweet = []
            try:
                for modelId in modelIds:
                    allModelProbas4Tweet.append(tweet[modelId + '_proba'])
            except:
                raise Exception("Probabilistic results for model id in ensemble model_id_list is not in tweet")
            #sum all model probabiliies and produce mean value per Webis paper
            sumModelProbsList = map(lambda sublist: sum(sublist), itertools.izip(*allModelProbas4Tweet))
            meanProbs = map(lambda probSum: round(probSum/len(modelIds),3),sumModelProbsList)
            #get winning idx, class and probability
            winningIndex = meanProbs.index(max(meanProbs))
            winningClass = ensemble["model_classes"][winningIndex]
            winningProba = meanProbs[winningIndex]
            tweet[ensemble["id"] + "_discrete"] = winningClass
            tweet[ensemble["id"] + "_proba"] = winningProba
            listOfTweetDicts[idx] = tweet
        
    return listOfTweetDicts


