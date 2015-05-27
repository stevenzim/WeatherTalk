 Kaggle Competition
==============   
 Random Acts of Pizza
--------------   
    The included code in this project is to produce predictions for the Kaggle
    "Random acts of pizza" competition:
    (https://www.kaggle.com/c/random-acts-of-pizza).
    
    Usage: in a command line run "python main.py"
    
Requirements:
--------------  
-   scikit learn version 0.14.1 or later
-   nosetests
-   nltk with latest data packages (see: see http://stackoverflow.com/questions/17672423/http-proxy-authentification-error-for-nltk-download for steps to update path if necessary)  


main.py(inputs)
--------------    
    In this file, you can update the following parameters: 
- Training and Test File locations
- Paths to output for models, evaluations results and kaggle submission file
- Name of your model
- Additional features to include beyond the baseline features
- **MOST IMPORTANT: You can choose your classifier** 


Outputs
--------------  
    With these parameters specified, the program will output to the path:
-   CSV file for submission to Kaggle
-   Model Evaluation Files for Review
-   Binary files to predict results for new Reddit Posts

    For full details of the system and results, please see the included report
    on our system.  
    
    **Note Also: This system and code can be adapted for similar problems**
    
    
Pipeline
-------------
    **"import raop pipeline"**  This module contains functions to preprocess data
    and extract features.  Check out doc strings and code for details.
