

#TODO: BIG ITEMS - Grid Search with options dictionary

#EXAMPLE 0 - Extract NLP Triples
from twxeety import pipeline
inFile = 'resources/SemTrain.json'
outFile = 'resources/SemTrainTriples.json'
pipeline.extractTweetNLPtriples(inFile,outFile)


#EXAMPLE 1 - MY FIRST PIPELINE WITH FEATURE UNION
from twxeety import helper
from twxeety import transformers as tran
import string
from sklearn.pipeline import (Pipeline,FeatureUnion)
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import (CountVectorizer, TfidfTransformer, TfidfVectorizer)
from sklearn.linear_model import SGDClassifier
from sklearn.grid_search import GridSearchCV
ngramCountPipe = Pipeline([\
            ('docs',tran.DocsExtractor()),\
            ('count',tran.CountVectorizer(analyzer=string.split))])

ngramTfidfPipe = Pipeline([\
            ('docs',tran.DocsExtractor()),\
            ('tf-idf',tran.TfidfVectorizer(analyzer=string.split))])

otherFeaturesPipe = Pipeline([\
            ('text-feats-dict',tran.TextFeaturesExtractor()),\
            ('text-feats-vec',tran.DictVectorizer())])

features = FeatureUnion([
            ('ngrams',ngramCountPipe),
            ('others',otherFeaturesPipe)])

pipeline = Pipeline([\
            ('features',features),
            ('clf',SGDClassifier())])

#1a - extract triples and ys
inFile = 'tests/test-data/SemEval/3-SemEvalFeatures.json'
data = helper.loadJSONfromFile(inFile)           
ed = tran.TriplesYsExtractor()
triplesList, ysList = ed.transform(data,ysKeyName = 'sentiment_num')

#1b - display ngram vector for Tfidf and otherFeaturs Vector
ngramsTfidf = ngramTfidfPipe.fit_transform(triplesList)
ngramsTfidf.toarray()
otherFeatures = otherFeaturesPipe.fit_transform(triplesList)
otherFeatures.toarray()

#1c - feature Union of ngramCounts and extra features
allFeatures = features.fit_transform(triplesList)
allFeatures.toarray()


#EXAMPLE 2 - GRIDSEARCH
#Modified version by Steven Zimmerman
# Original from http://scikit-learn.org/stable/_downloads/grid_search_text_feature_extraction.py
# ORIGINAL Authors: Olivier Grisel <olivier.grisel@ensta.org>
#         Peter Prettenhofer <peter.prettenhofer@gmail.com>
#         Mathieu Blondel <mathieu@mblondel.org>
# License: BSD 3 clause

from twxeety import helper
from twxeety import transformers as tran
import string
from sklearn.pipeline import (Pipeline,FeatureUnion)
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import (CountVectorizer, TfidfTransformer, TfidfVectorizer)
from sklearn.linear_model import SGDClassifier
from sklearn.grid_search import GridSearchCV

from __future__ import print_function

from pprint import pprint
from time import time
import logging



print(__doc__)

# Display progress logs on stdout
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')
                    
###GET DATA
inFile = 'resources/SemTrainTriples.json'
data = helper.loadJSONfromFile(inFile)           
ed = tran.TriplesYsExtractor()
triplesList, ysList = ed.transform(data,ysKeyName = 'sentiment_num')

# define a pipeline combining a text feature extractor with a simple
# classifier
pipeline = Pipeline([
    ('docs', tran.DocsExtractor()),
    ('vect', CountVectorizer(analyzer=string.split)),
    ('tfidf', TfidfTransformer()),
    ('clf', SGDClassifier()),
])

# uncommenting more parameters will give better exploring power but will
# increase processing time in a combinatorial way
parameters = {
    #'vect__analyzer':(string.split),
    'vect__max_df': (0.5, 0.75, 1.0),
    #'vect__max_features': (None, 5000, 10000, 50000),
    'vect__ngram_range': ((1, 1), (1, 2)),  # unigrams or bigrams
    #'tfidf__use_idf': (True, False),
    #'tfidf__norm': ('l1', 'l2'),
    'clf__alpha': (0.00001, 0.000001),
    'clf__penalty': ('l2', 'elasticnet'),
    #'clf__n_iter': (10, 50, 80),
}


if __name__ == "__main__":
    # multiprocessing requires the fork to happen in a __main__ protected
    # block
    # find the best parameters for both the feature extraction and the
    # classifier
grid_search = GridSearchCV(pipeline, parameters, n_jobs=-1, verbose=1)

print("Performing grid search...")
print("pipeline:", [name for name, _ in pipeline.steps])
print("parameters:")
pprint(parameters)
t0 = time()
grid_search.fit(triplesList, ysList)
print("done in %0.3fs" % (time() - t0))
print()
print("Best score: %0.3f" % grid_search.best_score_)
print("Best parameters set:")
best_parameters = grid_search.best_estimator_.get_params()
for param_name in sorted(parameters.keys()):
    print("\t%s: %r" % (param_name, best_parameters[param_name]))


#vvvvvvvvvvvvOTHER USEFUL EXAMPLESvvvvvvvvvvv
import twxeety.pipeline as pipeline
import twxeety.helper as helper
testFile = 'tests/test-data/SemEval/3-SemEvalFeatures.json'
X, y = pipeline.loadTweetFeaturesToNumpy(testFile,0)


import string #necessary for analyzer option, to split unicode and strings
import sklearn
from sklearn.feature_extraction.text import (CountVectorizer,TfidfTransformer,TfidfVectorizer)


#simple string split on corpus to learn dictionary
#dictionary is then dumped to json
vectorizer =  CountVectorizer(analyzer=string.split, min_df=1) #string.split is a trick mentioned in scikit section4.2.3.10.
unigrams  = vectorizer.fit_transform(X)
vocab = vectorizer.vocabulary_
helper.dumpJSONtoFile('tests/test-data/SemEval/SemEvalVocabulary.json',vocab)

#TFidf vectorizer
vectorizer =  TfidfVectorizer(analyzer=string.split, min_df=1) #string.split is a trick mentioned in scikit section4.2.3.10.
unigrams  = vectorizer.fit_transform(X)
vocab = vectorizer.vocabulary_


#load vocabulary from json file
#necessary to vectorize unseen data
vocabFile = 'tests/test-data/SemEval/SemEvalVocabulary.json'
vocab = helper.loadJSONfromFile(vocabFile)
vectorizer =  CountVectorizer(analyzer=string.split, min_df=1,\
                vocabulary = vocab) 
X2 = X
X2.append('happy happy :) :) no') #append a new unseen example
unigrams  = vectorizer.fit_transform(X2)
unigrams.toarray()  #now you will see added on vector with new word counts, still with original dictionary













