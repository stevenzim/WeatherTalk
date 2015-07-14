'''
AUTHOR: Steven Zimmerman
Date: July 14th 2015

Purpose: To convert various sentiment lexicons into desired JSON/dictionary format
'''

from wxtalk import helper


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
