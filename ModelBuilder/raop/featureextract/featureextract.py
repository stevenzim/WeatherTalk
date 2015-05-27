import re
import datetime
import numpy as np

class FeatureExtract(object):
    '''
    This class contains modules that extract features from the dataset
    which are:
    findEvidence - find post with image/proof
    evalStatus - status of the requester
    identifyNarratives - the number of terms in different kinds of stories/narratives
    identifyReciprocity - Detect phrases that relates to the concept of "paying kindness forward"
    countWord - the total number of words  of the request
    getTime - unix timestamp of the request subtracted by the global minimum timestamp of all datasets 
    getFirstHalf - check whether the request was made at the first half of the month or not
    '''
    def  __init__(self):
        self.evidence = None
        self.statusKarma = None
        self.statusAccAge = None
        self.statusPrevAct = None
        self.narrativeCountMoney1 = None
        self.narrativeCountMoney2 = None
        self.narrativeCountJob = None
        self.narrativeCountFamily = None
        self.findReciprocity = None
        self.wordNum = None
        self.minTime = None
        self.time = None
        self.firstHalf = None
        
        
        #can's additions 13MAR
        self.narrativeCountMoney1Bin = None
        self.narrativeCountMoney2Bin = None
        self.narrativeCountJobBin = None
        self.narrativeCountFamilyBin = None 
        self.median_money1= None
        self.median_money2= None
        self.median_job= None
        self.median_fam= None

    def findEvidence(self,request_text_edit_aware):
        '''Find reddit post with image/proof
        On roap, users often post thier photo/video 
           as an evidence of thier condition/existence
        this module uses regex library (re) to parse
        url from imgur and youtube
           As well as url with jpg and png file 		
        1 - evidence is found
           0 - evidence is not found
        '''

        regex = re.compile(r"([Hh]ttp(\S)+((imgur)|(youtube))(\w|\W)+)|([Hh]ttp(\S)+((jpe?g)|(png)))")
        match = re.search(regex,request_text_edit_aware)	
        if match: 	
            self.evidence = 1
        else :
            self.evidence = 0

    def evalStatus(self,requester_upvotes_minus_downvotes_at_request, \
	requester_account_age_in_days_at_request, requester_number_of_comments_in_raop_at_request,\
	requester_number_of_posts_on_raop_at_request):
        '''evaluate the status of the requester
           statusKarma = overall karma point at request time
           statusAccAge = account age at request time
           statisPrevAct 1-->previously active on raop, else 0
        '''
        self.statusKarma = requester_upvotes_minus_downvotes_at_request
        self.statusAccAge = requester_account_age_in_days_at_request
        self.statusPrevAct = 1 if requester_number_of_comments_in_raop_at_request + \
        requester_number_of_posts_on_raop_at_request > 0 else 0


    def identifyNarratives(self,request_text_edit_aware):
        '''Count the number of terms in different kinds of stories using regular expression: Money1 Money2 Job Family
          As suggested on http://cs.stanford.edu/~althoff/raop-dataset/altruistic_requests_icwsm.pdf
        '''
        money1_regex = re.compile(r"(week|ramen|paycheck|work|couple|rice|check|pizza|grocery|rent|anyone|favor|someone|bill|money)")
        money2_regex = re.compile(r"(food|money|house|bill|rent|stamp|month|today|parent|help|pizza|someone|anything|mom|anyone)")
        job_regex = re.compile(r"(job|month|rent|year|interview|bill|luck|school|pizza|paycheck|unemployment|money|ramen|end|check)")
        family_regex = re.compile(r"(tonight|night|today|tomorrow|someone|anyone|friday|dinner|something|account|family|bank|anything|home|work)")

        money1_match = re.findall(money1_regex,request_text_edit_aware)
        money2_match = re.findall(money2_regex,request_text_edit_aware)
        job_match = re.findall(job_regex,request_text_edit_aware)
        family_match = re.findall(family_regex,request_text_edit_aware)

        self.narrativeCountMoney1 = len(money1_match)
        self.narrativeCountMoney2 = len(money2_match)
        self.narrativeCountJob = len(job_match)
        self.narrativeCountFamily = len(family_match)

    def identifyReciprocity(self, request_text_edit_aware):
        '''
        Detect phrases that relates to the concept of "paying kindness forward" using regular expression
        1 - detected
        0 - not detected
        '''
        reciprocity_regex = re.compile(r"([Pp]ay [Ii]t [Ff]orward|[Rr]eturn [Tt]he [Ff]avor|[Rr]eciprocat.*)")
        if re.search(reciprocity_regex,request_text_edit_aware):
          self.findReciprocity = 1
        else:
          self.findReciprocity = 0

    def countWord(self,tokens):
        '''
        Count the total number of words  of the request
        '''
        self.wordNum = len(tokens)
    
    def getMinTime(self,timeList):
        '''
        Find the minimum timestamp in the dataset
        '''
        listofTime=[]
        for dict in timeList:
            listofTime.append(dict["unix_timestamp_of_request"])
        self.minTime=min(listofTime)

    def getTime(self,time):
        '''
        Subtract unix timestamp of the request by the global minimum timestamp of all datasets 
        '''
        #startTime = self.minTime
        startTime = 1297722537.0    #hard coding start time = global min for datasets
                                    #this only works for Kaggle raop data
                                    #This improved our Kaggle leader board position by 6 spots
        self.time = time-startTime

    def getFirstHalf(self,time):
        '''
        Uses unix timestamp to check whether the request was made at the first half of the month or not.
        1 - yes
        0 - no
        '''
        date=datetime.datetime.fromtimestamp(time)
        if(date.day < 16):
            self.firstHalf=1
        else:
            self.firstHalf=0
     
    def CountPOSTag(self, listOfTokensTags , POStag = None):
        '''
        Counts the number of occurences of specified POS tag
        listOfTokensTags = [['Thanks','NNP']['good','JJ'],['super','JJS']]
        POStag = JJ or NNS or something else
        '''
        count = 0 
        for item in listOfTokensTags:
            currentPOS = item[1]
            if re.search(POStag, currentPOS):
                count = count + 1
        
        return count        
                
    #can's additions
    def getMedianlist(self, thelist):#
        money1 = []
        money2 = []
        job = []
        fam = []
        for dict in thelist:
            self.countWord(dict["added_tokens"])
            self.identifyNarratives(dict["added_Title_+_Request"])
            money1.append(self.narrativeCountMoney1/float(self.wordNum))
            money2.append(self.narrativeCountMoney2/float(self.wordNum))
            job.append(self.narrativeCountJob/float(self.wordNum))
            fam.append(self.narrativeCountFamily/float(self.wordNum))    
	    self.median_money1=np.median(money1)
        self.median_money2=np.median(money2)
        self.median_job=np.median(job)
        self.median_fam=np.median(fam)		


    def identifyNarrativesBinary(self,request_text_edit_aware, wordCount):
        '''Count the number of terms in different kinds of stories using regular expression: Money1 Money2 Job Family
        As suggested on http://cs.stanford.edu/~althoff/raop-dataset/altruistic_requests_icwsm.pdf
        '''
        money1_regex = re.compile(r"(week|ramen|paycheck|work|couple|rice|check|pizza|grocery|rent|anyone|favor|someone|bill|money)")
        money2_regex = re.compile(r"(food|money|house|bill|rent|stamp|month|today|parent|help|pizza|someone|anything|mom|anyone)")
        job_regex = re.compile(r"(job|month|rent|year|interview|bill|luck|school|pizza|paycheck|unemployment|money|ramen|end|check)")
        family_regex = re.compile(r"(tonight|night|today|tomorrow|someone|anyone|friday|dinner|something|account|family|bank|anything|home|work)")

        money1_match = re.findall(money1_regex,request_text_edit_aware)
        money2_match = re.findall(money2_regex,request_text_edit_aware)
        job_match = re.findall(job_regex,request_text_edit_aware)
        family_match = re.findall(family_regex,request_text_edit_aware)

        self.narrativeCountMoney1Bin = 1 if (len(money1_match)/float(wordCount))>self.median_money1 else 0
        self.narrativeCountMoney2Bin = 1 if (len(money2_match)/float(wordCount))>self.median_money1 else 0
        self.narrativeCountJobBin = 1 if (len(job_match)/float(wordCount))>self.median_job else 0
        self.narrativeCountFamilyBin = 1 if (len(family_match)/float(wordCount))>self.median_fam else 0	
	

    

