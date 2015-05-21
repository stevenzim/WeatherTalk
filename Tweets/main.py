#Steven Zimmerman
#21-MAY-2015

#This is a cheap way to force data to be continually collected round the clock
#If the getRawTweets throws an error (e.g. if network connection is lost), 
#the while loop keeps going until getRawTweets stops throwing error
#NOTE: this is a "risky" way to program. 

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
