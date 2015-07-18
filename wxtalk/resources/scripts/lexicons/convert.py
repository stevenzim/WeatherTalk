'''
AUTHOR: Steven Zimmerman
Date: July 14th 2015

Purpose: To convert various sentiment lexicons into desired JSON/dictionary format

usage: from wxtalk.resources.scripts.lexicons import convert

'''

from wxtalk import helper
import codecs

def createNRCautoLexs(inFileName,outFileName):
    '''Given file name of original NRC list of automatically generated lexicons
    see section 3 from: http://www.saifmohammad.com/WebPages/lexicons.html
    returns a dictionary containing word/n-gram with PMI score'''
    iFile = open(inFileName,'r')
    outDict = {}
    for line in iFile:
        line = line.split('\t')
        #set term and score in dict
        outDict[line[0]] = line[1]
    iFile.close()
    helper.dumpJSONtoFile(outFileName,outDict)
    
    
def createBingLiu(posFileName='positive-words.txt',negFileName='negative-words.txt',outFileName='BingLiu.json'):
    '''Given file names of original BingLiu files, load into dictionary where positive terms = 1.0 and neg terms = -1.0.
    If they occur in both lists, set = 0.0
    These values per discussion with NRC group'''
    posFile = open(posFileName,'r')
    #NOTE: I have had to manually change this in original file as it had wrong encoding.
    negFile=codecs.open(negFileName, encoding='utf-8')
    
    outDict = {}
    
    #load positive terms/score
    for line in posFile:
        line = line.strip()
        #set term and score in dict
        outDict[line] = 1.0
    posFile.close()
    
    #load neagtive terms/score
    for line in negFile:
        line = line.strip()
        #set term and score in dict
        if line in outDict.keys():
            outDict[line] = 0.0
        else:
            outDict[line] = -1.0
    negFile.close()
    
    helper.dumpJSONtoFile(outFileName,outDict)
    
def createMPQA(inFileName='mpqa.tff',outFileName='MPQA.json'):
    '''Given file name of original MPQA files, load into dictionary where positive terms = 1.0 and neg terms = -1.0.
    If they occur in both lists, set = 0.0
    These values per discussion with NRC group'''
    # example line: type=weaksubj len=1 word1=abandoned pos1=adj stemmed1=n priorpolarity=negative
    iFile = open(inFileName,'r')
    outDict = {}
    for line in iFile:
        elements = line.split(' ')
        elements = elements[2] + '=' + elements[-1]  #get the word and polarity elements and make it look like --> 'word1=abandoned=priorpolarity=negative'
        elements = elements.split('=') #split elements --> looks like --> ['word1', 'abandoned', 'priorpolarity', 'negative']
        elements = map(lambda x: x.strip(),elements) #clean up unwanted characters i.e. carriage returns and whitespace
        
        #set term and score in dict
        if elements[1] in outDict.keys():
            if (outDict[elements[1] ] == -1.0) and (elements[-1] == 'positive') or\
                (outDict[elements[1] ] == 1.0) and (elements[-1] == 'negative'):
                if elements[-1] == 'neutral':
                    pass
                else:
                    outDict[elements[1] ] = 0.0
                    continue
        if elements[-1] == 'positive':
            outDict[elements[1]] = 1.0
        elif elements[-1] == 'negative':
            outDict[elements[1]] = -1.0
        else:
            continue
    iFile.close()
    helper.dumpJSONtoFile(outFileName,outDict)    
    
    
def createNRCemotions(inFileName='NRC-emotion-lexicon.txt',outFileName='NRC-emotion.json'):
    '''Given file name of original NRC file, load into dictionary where positive terms = 1.0 and neg terms = -1.0 or 0.0 for neither
    These values per discussion with NRC group'''
    # example lines:
    # aback	anger	0
    # aback	anticipation	0
    # aback	disgust	0
    # aback	fear	0
    # aback	joy	0
    # aback	negative	0
    # aback	positive	0
    # aback	sadness	0
    # aback	surprise	0
    # aback	trust	0
    iFile = open(inFileName,'r')
    outDict = {}
    for line in iFile:
        elements = line.split('\t')
        elements = map(lambda x: x.strip(),elements) #clean up unwanted characters i.e. carriage returns and whitespace
       
        #print elements
        #set term and score in dict
        if (elements[0] in outDict.keys()) and (elements[-1] =='1') and \
        ((elements[1] == 'positive') or (elements[1] == 'negative')):
            outDict[elements[0] ] = 0.0
            continue
        if elements[1] == 'positive':
            if elements[-1] == '1':
                outDict[elements[0]] = 1.0
        if elements[1] == 'negative':
            if elements[-1] == '1':
                outDict[elements[0]] = -1.0
    iFile.close()
    helper.dumpJSONtoFile(outFileName,outDict)   
    
def createKLUE(fileName='emoticons_wikipedia.txt',emotiFile='KLUEemoticon.json',acroFile='KLUEacronym.json'):
    #TODO: Seperate emoticons and acronyms
    '''Put KLUE emoticons/acronym/senti scores in appropriate dicts and write to file'''
    iFile = open(fileName,'r')
   
    emoticonDict = {}
    acronymDict = {}
    
    acronyms = False
    #load emoticons/terms/score
    for line in iFile:
        line = line.split()
        if line[0] == '10q':
            acronyms = True
        if acronyms == False:
            #set term and score in emoticon dict
            if line[1] == 'positive':
                emoticonDict[line[0]] = 1.0
            else:
                emoticonDict[line[0]] = -1.0
        else:
            #set term and score in acronym dict
            if line[1] == 'positive':
                acronymDict[line[0]] = 1.0
            else:
                acronymDict[line[0]] = -1.0
    iFile.close()
    
    helper.dumpJSONtoFile(emotiFile,emoticonDict)
    helper.dumpJSONtoFile(acroFile,acronymDict)
