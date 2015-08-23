#script to build CMU cluster vocabulary and lexicon used for feature extraction
'''
with cmu cluster file
1- built a vocabulary to load into CountVectorizer should be 1000 cluster vals  Key = binary value Val = feature number
2- created a lexicon/dictionary with key = token and val equal to binary value
3- For each tweet build a string of binary cluster vals that can be split on string.split.   If token not in lexicon, add nothing to list
'''

from wxtalk import helper
origFile = open('50mpaths2Cluster.txt','r')

outputVocab = {}
outputLexicon = {}

for line in origFile:
    line = line.split()
    outputVocab[line[0]] = None
    outputLexicon[line[1]] = line[0]


vocabKeys = outputVocab.keys()
clusterVals = set(vocabKeys)

index = 0
for clusterCode in clusterVals:
    outputVocab[clusterCode] = index
    index +=1


helper.dumpJSONtoFile('CMU-cluster-vocab.json',outputVocab)
helper.dumpJSONtoFile('CMU-cluster-lexicon.json',outputLexicon)
    
