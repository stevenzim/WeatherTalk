import helper
origFile = open('50mpaths2Cluster.txt','r')

outputVocab = {}
outputLexicon = {}

for line in origFile:
    line = line.split()
    outputVocab[line[0]] = None
    outputLexicon[line[1]] = line[2]
   
   
clusterVals = set(outputVocab.keys().sort())

index = 0
for clusterCode in clusterVals:
    outputVocab[clusterCode] = index
    index +=1

helper.dumpJSONtoFile('CMU-cluster-vocab.json',outputVocab)
helper.dumpJSONtoFile('CMU-cluster-lexicon.json',outputLexicon)
    
