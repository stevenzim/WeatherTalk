from TwitterAPI import TwitterAPI
import json
import datetime

	
def getTweets():
	api = TwitterAPI(consumer_key = 'wJqNYeJ4apokhjvUFAVPacYom', consumer_secret = 'RG8UyBEwZc8RtfmS9IXFigICUr9mewTMUJWQdpUc9J6gvh1H8I', access_token_key = '595669629-Oe5ocvFoRjwNnE3I7AfOVOzCTR2ac2raE5uVG7sE', access_token_secret = 'PPrhOb4myhPvC9ueAObTuoKIAiNsmsfIqzPeytcGUuRJM')
	#CONUS: request = api.request('statuses/filter', {'locations':'-124.7,24.4,-67,49'})
	#EASTERN MASS and RI and Nashua NH: request = api.request('statuses/filter', {'locations':'-73.0,40.0,-70,43.0'})
	request = api.request('statuses/filter', {'locations':'-73.0,40.0,-70,43.0'})
	utc_datetime = datetime.datetime.utcnow().strftime("%Y-%m-%d-%H%MZ")
	fileName = 'Tweets_%s.json' % utc_datetime
	totalTweets = 0
	tweetsThisFile = 0
	for currentTweet in request:
		utc = datetime.datetime.utcnow()
		totalTweets +=1
		if (totalTweets % 100) == 0:
			print totalTweets
		if (utc.minute % 30) == 0:
			if utc.second == 0:
				return 0
			utc_datetime = datetime.datetime.utcnow().strftime("%Y-%m-%d-%H%MZ")
			fileName = 'Tweets_%s.json' % utc_datetime
		json.dump(currentTweet, open(fileName,'a'), sort_keys=True, indent=4, separators=(',', ': '))


while True:
	try:
		getTweets()
	except:
		continue