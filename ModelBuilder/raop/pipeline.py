import raop.helper as helper
import raop.preprocess.preprocess as preproc
import raop.featureextract.featureextract as featureextract
import raop.model.ml as model
import numpy as np
import os
import re
import nltk
from sklearn.cross_validation import train_test_split as train_valid_split

#Step 1	- Remove desired keys from each dictionary
def removeNonNeededKeys(inputJSONfile,outputJSONfile):
	'''Removes keys from training file that are not needed.  
	The keys listed below are not in the test data and therefore not necessary in training data either.
	These fields are removed for readibility
	usage: removeNonNeededKeys("resources/train.json","resources/1-train-fields-removed.json")'''
	testInput = "resources/train.json"
	testOutput = "resources/1-train-fields-removed.json"
	keysToDrop = ["number_of_downvotes_of_request_at_retrieval", 
					"number_of_upvotes_of_request_at_retrieval", 
					"post_was_edited", 
					"request_number_of_comments_at_retrieval", 
					"request_text", 
					"requester_account_age_in_days_at_retrieval", 
					"requester_days_since_first_post_on_raop_at_retrieval", 
					"requester_number_of_comments_at_retrieval", 
					"requester_number_of_comments_in_raop_at_retrieval", 
					"requester_number_of_posts_at_retrieval", 
					"requester_number_of_posts_on_raop_at_retrieval", 
					"requester_user_flair",
					"requester_upvotes_minus_downvotes_at_retrieval", 
					"requester_upvotes_plus_downvotes_at_retrieval",]

	list = helper.loadJSONfromFile(inputJSONfile)
	for dict in list:				
		for key in keysToDrop:
				dict.pop(key, None)	

	helper.dumpJSONtoFile(outputJSONfile, list)

###########################

#Step 2 - Add POS tags, tokens, etc to each dictionary
def addPreprocessedKeyVals(inputJSONfile,outputJSONfile):
	'''Loads json file to list --> creates object for each dictionary in list
	Then preprocesses the text data in dictionary (e.g. POS tags)
	Then creates new key value pairs with these processed fields
	usage: addPreprocessedKeyVals("resources/1-train-fields-removed.json","resources/2-train-preprocessed-keys-added.json")'''
	list = helper.loadJSONfromFile(inputJSONfile)
	#count = 1
	for dict in list:
		preProcObj = preproc.Preprocess()
		preProcObj.setDictionary(dict)
		preProcObj.concatenate("request_title", "request_text_edit_aware")
		preProcObj.sentSeg(preProcObj.concatText)
		preProcObj.tokenize(preProcObj.concatText)
		preProcObj.posTag(preProcObj.tokenizedText)
		preProcObj.normalisation(preProcObj.tokenizedText)
		dict["added_Title_+_Request"] = preProcObj.concatText
		dict["added_segmented_sentences"] = preProcObj.sentSegmentedText
		dict["added_tokens"] = preProcObj.tokenizedText
		dict["added_POStags"] = preProcObj.POS_TaggedText
		dict["added_normalised_text"] = preProcObj.normalisedText
		#print count
		#count += 1
	helper.dumpJSONtoFile(outputJSONfile, list)


###########################

#Step 3 - Extract Features / Create Feature Vectors


	
def getFeatures(inputJSONfile, isTest, xt_features_idxs = None):
    '''Loads Json(output from step 2) file to list --> creates object for 
       each dictionary in list. Then extract features from each dictionary,
       and keep it in a feature vector.
       '''
    thelist = helper.loadJSONfromFile(inputJSONfile)
    featObj = featureextract.FeatureExtract()
    X_set = []
    Y_set = []
    featObj.getMinTime(thelist)
    
    #can's change:
    featObj.getMedianlist(thelist)

    for dict in thelist:
        temp_feat = []
        temp_addit_feat =[]
        addit_feat_to_append = []
        
        #Base features
        #Populate the feature vector for each instance with base features
        # Evidence (proof on imgur,youtube,etc.) - 1-True/0-False
        # Status: Karma - Numerical(upvote - downvote)
        # Status: Account Age - Numerical (# of days as a member of reddit)
        # Status: Previously active on RAOP - 1-True  0 - False
        # Detected Narrative terms: Money 1 - Numerical (# of words)
        # Detected Narrative terms: Money 2 - Numerical (# of words)
        # Detected Narrative terms: Job - Numerical (# of words)
        # Detected Narrative terms: Family - Numerical (# of words)
        # Reciprocity : 1- True , 0 - False
        # Word Count : Numerical (number of words)
        # Time of request:
        # First half of the month: 1-True, 0 - False
        featObj.findEvidence(dict["added_Title_+_Request"])
        featObj.evalStatus(dict["requester_upvotes_minus_downvotes_at_request"],\
        dict["requester_account_age_in_days_at_request"],\
        dict["requester_number_of_comments_in_raop_at_request"],\
        dict["requester_number_of_posts_on_raop_at_request"])
        featObj.countWord(dict["added_tokens"])
        featObj.identifyNarratives(dict["added_Title_+_Request"])
        featObj.identifyNarrativesBinary(dict["added_Title_+_Request"],featObj.wordNum)
        featObj.identifyReciprocity(dict["added_Title_+_Request"])
       
        featObj.getTime(dict["unix_timestamp_of_request"])
        featObj.getFirstHalf(dict["unix_timestamp_of_request"])
        
        temp_feat.append(featObj.evidence)
        temp_feat.append(featObj.statusKarma)
        temp_feat.append(featObj.statusAccAge)
        temp_feat.append(featObj.statusPrevAct)
        
        temp_feat.append(featObj.narrativeCountMoney1)
        temp_feat.append(featObj.narrativeCountMoney2)
        temp_feat.append(featObj.narrativeCountJob)
        temp_feat.append(featObj.narrativeCountFamily)
        
        #can's changes to try
        #temp_feat.append(featObj.narrativeCountMoney1Bin)
        #temp_feat.append(featObj.narrativeCountMoney2Bin)
        #temp_feat.append(featObj.narrativeCountJobBin)
        #temp_feat.append(featObj.narrativeCountFamilyBin)
        
        temp_feat.append(featObj.findReciprocity)
        temp_feat.append(featObj.wordNum)
        
        temp_feat.append(featObj.time)
        temp_feat.append(featObj.firstHalf)

        #Additional Features
        #1 = num adjectives/num words
        temp_addit_feat.append(\
        float(featObj.CountPOSTag(dict["added_POStags"],'JJ')) / \
        float(featObj.wordNum))
        
        #2 = num adverbs/num words
        temp_addit_feat.append(\
        float(featObj.CountPOSTag(dict["added_POStags"],'RB')) / \
        float(featObj.wordNum))
        
        #3 = num adverbs/num words
        temp_addit_feat.append(\
        float(featObj.CountPOSTag(dict["added_POStags"],'NN')) / \
        float(featObj.wordNum))  
        
        #4 = num adverbs/num words
        temp_addit_feat.append(\
        float(featObj.CountPOSTag(dict["added_POStags"],'VB')) / \
        float(featObj.wordNum))    
        
        #5 = num of sentences                
        temp_addit_feat.append(len(dict["added_segmented_sentences"]))

        #6 = punctuation
        punct_regex = re.compile(r"(!)")
        punct_match = re.findall(punct_regex,dict['request_text_edit_aware'])
        temp_addit_feat.append(len(punct_match))
        
        #7 High likely stems that are true therefore count occurence
        stems_regex = re.compile(r"(supermarket|warn|batteri|fold|insurance|preciou|reasons|bonu|skip|insan|lil|struggling|admit|stapl|anticip|compens|constant|corpor|couldnt|deplet|familiar|interact|overal|pinch|pure|rut|shoulder|reserv|packag)")
        stems_match = re.findall(stems_regex,dict['request_text_edit_aware'])
        temp_addit_feat.append(len(stems_match))
        
        #8 stems binary only return 1 or 0
        if len(stems_match)>0:
            temp_addit_feat.append(1)
        else:
            temp_addit_feat.append(0)       
               
        #based on input list, add in the specified features.  numbers in list
        # must match the corresponding numbers in additional features list above
        if xt_features_idxs != None:
            for index in xt_features_idxs:
                addit_feat_to_append.append(temp_addit_feat[index-1])
                    
        #extend the feature vector with specified additional features            
        temp_feat.extend(addit_feat_to_append)        
        #add the feature vector to X set
        X_set.append(temp_feat)

        
        if isTest==0: # If the input json file is not the Kaggle test set
            # Append the requester_received_pizza label to the Y set      
            Y_set.append(dict["requester_received_pizza"])
     
    

    if isTest ==0:
        #return both X set and Y set, if the inputJSON is the trainning set
        return np.array(X_set), np.array(Y_set)
    else:
        #return only X set if the inputJSON is the Kaggle test set
        return np.array(X_set)
    
#####################
#Step 4 - Generic pipeline component to build model, save model, and output
#         evaluation metrics
def modelPipeline(classifier, X_set, Y_set,\
    modelOutpath, modelName, directoryName, description):
    '''
    INPUTS: 
    classifier = any sklearn classifier ex: GaussianNB()
    X_set = all features in numpy array format
    Y_set = all classifications in numpy array format (e.g. pizza True/False)
    
    modelOutpath = directory location of all models
    modelName = the name of model (perhaps a unique name)
    directoryName = the name of new directory to create your model
    description = full description of model (e.g. who ran it, date, features included)
    
    
    OUTPUTS:
    - Model binary files to specified directory
    - Report with details on model (e.g. Metrics such as F1/Precision, 
    cross-validation stats)
     
    '''
    #create Validation model & cross-valid metrics  
    #split training set into 80/20 split.  This will be useful for evaluation metrics
    X_train, X_valid , Y_train, Y_valid = train_valid_split(X_set,Y_set,test_size=0.2, random_state=42)
    modelObj = model.MLmodel(classifier, X_train, Y_train)
    modelObj.crossValidate()
    cvStats = modelObj.cv_accuracy
    cvStats = cvStats.tolist()
    modelObj.fitModel()

    #Create validation model predictions & calculate precision/recall/F1
    y_preds = modelObj.model.predict(X_valid)  #get predictions for model
    modelObj.evaluationResult(y_preds,Y_valid)

    #set output model to directory
    dirPath = modelOutpath + directoryName
    fullOutPath = dirPath + '/' + modelName
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)


    #####save report to directory#####
    reportFile = fullOutPath + '.report'
    oFile = open(reportFile,'w')

    #report information
    oFile.write('Model Name: ' + modelName + '\n')
    oFile.write('Model Description: ' + description + '\n')
    oFile.write('Model Feautures: ' + 'BASELINE FEATURES' + '\n\n')

    #prec/recall/f-1
    oFile.write('Model Evaluation Metrics\n')
    oFile.write('----------------------\n\n')
    oFile.write(modelObj.evalResult)
    oFile.write('\n\n----------------------\n\n')

    #cross-valid stats
    oFile.write('Cross Validation Stats\n')
    oFile.write('----------------------\n')
    i = 1
    foldTotal = 0.0
    for fold in cvStats:
        oFile.write("Fold-" + str(i) + " = " + str(fold) + '\n')
        i += 1
        foldTotal += fold

    oFile.write('----------------------\n')
    oFile.write("Average = " + str(foldTotal/(i-1)) + '\n')


    oFile.close()

    #RELOAD DATA and CREATE FINAL MODEL
    #reload training data and create model on 100% of training set
    modelObj = model.MLmodel(classifier, X_set, Y_set)
    modelObj.fitModel()
    
    #save final model
    modelObj.saveModel(fullOutPath)
