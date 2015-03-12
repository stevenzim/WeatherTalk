
import getRawTweets
import cleanTweets
import helper

rawTweetsPath = '1-RawTweets'


while True:
    try:
        if len(helper.getListOfFiles(rawTweetsPath)) > 10:
            cleanTweets.getRawTweets()
        else:
            getRawTweets.getTweets()
    except:
        continue