# Data CookBook for MindTrails Project

Last update: 3/23/2017

## Data Check List before launching

#### Make sure that your program has all the measurements that you plan to include

  1. **Print out the Standard Schedule Sheet (*SSS*).** Are all your trainings and measurements included and ordered as your plan?

    Address for *SSS* : [server path] + 'api/study', admin login required. [server path] could be found in the *server.config* file. Example:

    > https://mindtrails.virginia.edu/templeton/api/study

    **Note:** Please make sure the *SSS* match your study design before testing or piloting. For older version, you should do similar checking on the web source code.

  2. **Compile a codebook** for your study. Go over your source code, and compile a complete codebook that documents:
    - **Variable ID** for each items from each measure/training
    - **Corresponding questions** for each variable
    - **Value chart** for each variable

      and other information like:
    - **Citation** for measurements
    - **Scoring methods** for each measurements
    - **Logs** for change in variables across iterations

    **Note:** See [Example]() for a codebook example. You are encourage to do this before testing/piloting.
  2. **Go to your data folder** after the testing/piloting start. Do you get all the data files that you are expecting?

    Path for data folder could be found in your *server.config* file.

    Example:
    ```
    active_data/
    ├── AnxietyTriggers_Apr_14_2016.csv
    ├── AnxietyTriggers_Jan_28_2016.csv
    ├── AnxietyTriggers_Sep_07_2016.csv
    ...
    ├── TrialDAO_Apr_14_2016.csv
    ├── TrialDAO_Apr_24_2016.csv
    ├── TrialDAO_Jan_28_2016.csv
    ├── Trial_Sep_07_2016.csv
    ├── Visit_Sep_07_2016.csv
    ├── benchMark.json
    └── benchMark.txt
    ```

    **Note:** In newer version of MindTrails, you can use the ```MTData report``` command to generate a quick check. Please note that ```MTData report``` relies on a correct *SSS*. Please make sure that you have done the previous step before using ```MTData report```. See [*MTData*](http://mtdata.readthedocs.io/en/latest/ 'MTData') for more details.

    Example:

    > $ MTData report scale templeton_aws

    Output:
    ```
                         data_found entries_in_log entries_in_dataset  missing_rate
Demographics              True             21                 40  -0.904761905
MentalHealthHistory       True             20                 17   0.150000000
WhatIBelieve              True             26                 26   0.000000000
Phq4                      True             26                 34  -0.307692308
Affect                   False            NaN                NaN           NaN
scenarios                False            NaN                NaN           NaN
Relatability              True             25                 31  -0.240000000
ExpectancyBias            True             27                 25   0.074074074
HelpSeeking               True              1                  1   0.000000000
Evaluation               False            NaN                NaN           NaN
    ```

#### Make sure that your all your tables are recording data the way you want
1. **Do you have all the variables?**

  Look at the tables one by one, and find out:
  - Does it include **all the variables** in your corresponding questionnaire?    
  - Does it has a **participant id** column?
  - Is there **duplication in variable names** across tables?
  - If it is a **recurrent measures**, does the table include a **session** or a **pre/post** column/label or some sort?
  - If it is needed, does it include a **time stamp** column?

    ......

  **Note:** Use the [**codebook**](#make-sure-that-your-program-has-all-the-measurements-that-you-plan-to-include:) you compile earlier, your **data tables**, and your **web source code** to cross-reference the variable coding. *Make sure that they all match each other.*

2. **Does the ranges of variables look right?**

  A simple ```summary()``` in R/Python/SPSS would give you basic metrics of all the variables, and then look for anomalies including but not limited to:
  -  Does the **range of a variables** match the range by design?

    For example, if a measure ranges from 1 to 5 and "Prefer not to answer" is coded as -1, then there shouldn't be 0s in your table.

  - Are you getting the **variations** as you would expected?

    For example, are you getting all 0 or 1 or NA?

3. **Does the number of entries match your cases?**

  For each table, do counts and counts by group with ```count()``` and ```groupby.count()```, ask yourself these questions:
  - Does the **total number of entries match** *across tables*?
  - Does it **match the number of accounts and logs** you have from the system?

  If it doesn't (unfortunately it is ususally the case), then, **did these mismatches happen *systemmatically*?**

  **Systemmetical mismatch** includes situations like:
  - You are missing data **only for a period of time**.

    For example, no enteries are recorded during Mar 3 to present.
  - You are missing data **proportionally/only for one or some conditions**.

    For example, if you are missing a third of records in a specific table, it will be worth to check if those missings are all from participants in the same condition.

  - You are missing data **only for a specific session**.

    In this case, something might go wrong in your *SSS*.

  **Note:** In newer version of MindTrails, you can use the ```MTData report``` command to generate a quick check. Please note that ```MTData report``` relies on a correct *SSS*. Please make sure that you have checked *SSS* carefully before using ```MTData report```. See [*MTData*](http://mtdata.readthedocs.io/en/latest/ 'MTData') for more details.

  Example:
  > $ MTData report client templeton_aws

  Output:
  ```
  Checking completed.
Number of participants finished as least a task: 52.

   current_session         current_task  participant_id  task_no  \
0     PostFollowUp         WhatIBelieve             2.0      6.0   
1    fourthSession               Affect             3.0     26.0   
2    fourthSession                 Phq4             4.0     30.0   
3     firstSession            scenarios             5.0      6.0   
4     thirdSession       ExpectancyBias             6.0     15.0   
......
47   secondSession               Affect            50.0      NaN   
48    thirdSession               Affect            51.0      NaN   
49   fourthSession               Affect            52.0      NaN   
50    PostFollowUp       ExpectancyBias            53.0      NaN   
51             NaN                  NaN             1.0     12.0   

    target_task_no  Missing_no  
0               28        22.0  
1               19        -7.0  
2               25        -5.0  
3                5        -1.0  
4               18         3.0   
......  
47               9         NaN  
48              15         NaN  
49              19         NaN  
50              27         NaN  
51              -1       -13.0
  ```
