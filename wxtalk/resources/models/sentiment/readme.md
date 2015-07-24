Run Tweet extractor on tweets with NLP triples
Tweet extractor options are defaulted to have all URL/USERS removed and no digit/hashtag normalisation
For all available sentiment models binaries, URL/USERS removed, other options described below
GUMLT - trained with digitNormalise = True
KLUE -trained with hashNormalise = True
NRC & TeamX - defaults


Example usage for sentiment tagging--
from wxtalk.modelbuilder import transformers as tran
from wxtalk import helper

helper.extractTweetNLPtriples(rawTweeetJSONFile,tripleJSONFile)  #Raw Tweets --> Triple Tweets
loadedpipe = joblib.load('../../path to desired binaries')
data = helper.loadJSONfromFile(tripleJSONFile)
ed = tran.TweetTransformer(userNorm = None,urlNorm = None,hashNormalise=False,digitNormalise=False)
triplesList = ed.transform(data)
predicted_ys = loadedpipe.predict(triplesList)
sentimentList = predicted_ys.tolist()
count = 0 
for dict in data:
    keydropped = dict.pop("tagged_tweet_triples",None)  #stored as variable in order to supress print to screen
    dict["sentiment_score"] = sentimentList[count]
    count += 1

helper.dumpJSONtoFile(classifiedTweetFileName,data)
