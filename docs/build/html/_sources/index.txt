About MindTrails Data
======

A command-line tool that handle data exporting, decrypting and basic checking for
mindtrails or mindtrails-like website. Support multiple websites data collecting. It also contains toolbox for data analysis.

**For Example:**

```sh
# download and delete all the deleteable questionnaire entries on multiple servers
$ MTData export . .

# or

$ MTData export

# download all the questionnaire entries that should not be deleted from the templeton server.
$ MTData export templeton static

# Generate data checking tables that calculate the percentage of missing data for each column by questionnaire, for all.
$ MTData report scale

# Generate data checking tables that calculate the percentage of missing questionnaire for each participant in mindtrails project(servers)
$ MTData report client mindtrails
```

You could also create simple bash script with these tools to setup their export, decode and report schedule.

Getting Started
============

Download
---------

You can download it [here](https://github.com/Diheng/MTData) or type this in your command-line:
```sh
$ git clone https://github.com/Diheng/MTData.git
```

Installation
---------

Create a virtual environment with python 2.7, and install dependencies
(see http://docs.python-guide.org/en/latest/dev/virtualenvs/)
```bash
    $ virtualenv venv           
    $ source venv/bin/activate
    $ python setup.py install
    $ cd config
    $ cp server.config.example server.config
    $ cp log.config.example log.config
```

Configuration
---------

Create needed config and keys files. They should be place in folders within MTData, like this:

```
MTData/
├── MTData           <- actual codes
│   ├── com.py
│   ├── export.py
│   ├── export_old.py
│   ├── helloworld.py
│   ├── recovery.py
│   └── scales.py
├── README.md
├── bin
│   └── martin.sh
├── config           <- configuration files. In actural phrase, use \*.config instead of \*.config.sample
│   ├── export.config
│   ├── log.config
│   ├── recovery.config
│   ├── recovery_log.config
│   └── server.config
├── docs
├── keys             <- Keys for decrypting
│   ├── private_2.pem
│   └── private_1.pem
├── requirements.txt
├── setup.py
└── tests
```

Edit the server.config and log.config as needed.

Here is an example of server.config with comments:
```yaml
# create a new block for each new study you launch. Assign a name to it.
name_of_server1:
  # READY variables tells MTData whether it should export data for this study. Change it to True when you are ready.
  READY: False
  # DELETE_MODE tells MTData if it should delete deleteable entries on server.
  DELETE_MODE: False
  # SERVER: where you host your study. Remember to add '/api/exort' at the end of url.
  SERVER: 'https://MindTrails.virginia.edu/api/export'
  # Put in the account information of an admin account.
  USER:
  PASS:
  # Name of the key files for decrypting, you should have the actual files in the MTData/keys folder.
  PRIVATE_FILE:
  # This is for the time stamp on output csv files. You don't need to change it.
  DATE_FORMAT: "%b_%d_%Y"
  TIME_FORMAT: "%H_%M_%S"
  # Absolute path for the folder where you want to store your exported data. You should make a separated folder for each study.
  PATH: "/Users/X/Data_pool/name_of_server1/"

name_of_server2:
  READY: True
  DELETE_MODE: False
  SERVER: 'http://localhost:9000/api/export'
  USER:
  PASS:
  PRIVATE_FILE: 'key_for_decrypt.pem'
  DATE_FORMAT: "%b_%d_%Y"
  TIME_FORMAT: "%H_%M_%S"
  PATH: "/Users/Diheng/Box Sync/TEST_Diheng/"
```
**Note for 'READY'**
You can override READY:False in ```report``` and ```decode``` by specifying the name of server, but you *CANNOT* export a server's data if READY is False at any time.

**Note for 'deleteable'**
In mindtrails, all tables have a 'deleteable' attribute. 'deleteable' is True when this table contains sensitive data that you don't want to keep on your front end server, and therefore requires to be downloaded and deleted frequently(like, every 5 minutes). 'deleteable' is False when this table is needed for the online study constantly(like, baseline score for alarming, task logs needed for reference).

Here is an example of log.config with comments:
```yaml

```
Not yet done, please see log.config.sample for now.


Structure your data folders
----------

Create folders for your studies. They should looks like this:

```
Data_pool
├── logs    <- All website share one log folder
├── name_of_server1  
│   ├── active_data     <- for the csv files we decoded from raw_data
│   ├── raw_data        <- for the json files we saved from export. BenchMark file sits here as well.
│   └── reports         <- for the data checking report we generated based on active_data
├── name_of_server2
│   ├── active_data
│   ├── raw_data
│   └── reports
└── name_of_server3
    ├── active_data
    ├── raw_data
    └── reports
```

Setup routine
----------

Once you have done the installation and configuration, you can now write your own bash file and set up your own data managing routine:
First you write a **download.sh**:
```sh
#!/bin/bash
# download all deleteable data from all server.
MTData export . .
```

Then you edit your **crontab** by:
```sh
$ crontab -e
```
Add a line to crontab:
```sh
*/5 * * * * /Path/to/your/download.sh
```
Similarly you can create routine to do the needfuls.




## Current Usage

  - export

  ```sh
  $ MTData export [serverName, default=.(All)] [scaleName =./static/All]

  ```

  - decode

  ```sh
  $ MTData decode [serverName, default=.(All)] [scaleName, default=.(All)]
  ```

  - report
  ```sh
  $ MTData report client [serverName, default=.(All)]
  $ MTData report scale [serverName, default=.(All)]
  ```



## TODO:
1. Finish all the basic functions(export, decode, report)
  - export <- Done.
  - decode <- Done.
  - report <- Done, not yet tested*

2. Make the functions to be commend line tools and test them.  <- Done.

3. Make the code more concise by re-using (instead of copy&paste) methods. <- not yet done.

3. Redesign the logging system. <- not yet done.

3. Deploy to server and test it in commend line(currently, the .py files are called with python.) <- not yet done.

4. Update documentation. <- Done.

*Extra: Toolbox for data analysis*
We could add small tools that make our data analysis less boring and a lot faster. For example, almost all the questionnaire need to be scored and transform, so we have a scale.py that has the definition for the common actions shared with every scale. Each scale could have there own definition of action as well.

**Example:**
- tools.py  <- Tools that could be used in different situation.
- Scale.py <- has the function of score and trans, I used it for scoring. Need to be extended*

Also, we could write function that do basic analysis that we would need for time to time. For example, we would need to generate a attrition rate report pretty often. Diheng has python codes that works with pandas and Sam probably has tons of R code as well, which could be turn into python small tools pretty easily.*

**Let Diheng or Sam know if you would like to work on getting the most frequently used analysis codes into small tools.**

*All the items that end with a * would apprecitate helps!*










## Basic Overview

What this little application is going to do:

1. Read in a data package (oneShot).

1. One by one, read out the data form names(scale names) in oneShot, and then:

    A. Check if there is a file named [form_name]_[date].csv in the Active Data Pool, if not, create one

    B. Open [form_name]_[date].csv, append the data we have into it, one by one.

    C. Keep the raw data, and then send back delete commend one by one

    D. Close file, Log down the action and output to log files. If there is an error, email admin.



## Data requesting

Data requesting is done via the requests module, basic documentation could be found here:

http://docs.python-requests.org/en/latest/



## Data writing

Data writing is doen via the csv module, basic documentation could be found here:

https://docs.python.org/2/library/csv.html#csv-fmt-params



## Logging

Logging is done via the logging module. Configuration is through log.config. ALL temple and account information should
configure via log.config. See comments for reminder.

Bugs: MAKE SURE THAT YOU HAVE A "logs" FOLDER IN THE STORAGE PATH BEFORE YOU RUN THE PROGRAM. IT IS A STUPID BUG THAT I DON'T KNOW HOW TO FIX.

### Logging behaviors list below:

     A. There are five level of logging information, from low to high in priority are: debug/info/warning/error/critical

     B. All information will be stored in DEBUG.log.

     C. All information belong to and beyond info level will be stored in Daily.log.

     D. All information belong to and beyond warning level will be stored in error.log.

     E. All information reach critical level will be stored in bread_down.log, and emails will be sent to admin meanwhile.

     F. All log files will rotate at midnight. Old log files will be added suffix with local date. Log files will be
    rotating in a year long period(366 days).

### Break_down situation includes:

     A. Data request failure. Imply a network breakdown.

     B. Data delete failure. Imply a network breakdown and post a serious data security threat.

     C. Data writing failure. Imply a breakdown in csv module and need immediate attention.

Basic documentation about logging could be found here:

https://docs.python.org/2/library/logging.html



## Decrypting

    Original module. Need more documentation here:



## Backup system:

    Data backup is done by storing the raw data package in json format. Data will be stored daily.

     A. All new data package(quest within any oneShot) will be stored in
    raw_data/[scaleName]\_[Date].json before they are decrypted and recorded into active_data/[scaleName]\_[Date].csv.

     B. Raw data will be stored as json, and could be read as json objects.

     C. Keys for backup data are in form of [[scaleName] + '\_' + TIME].

     D. Backup data files is consistent with active data file in name and will be created in a daily base.

**HEADS UP**: *Creating new raw data files will not be logged into log files, but creating new active data files will.*



# Data deleting:

    Just so you know, turn on Delete mode by setting constant DELETE_MODE to True. (Highly NOT recommended in testing
    phrase.)

# BenchMark

	BenchMark is a file which contains the highest ID number(benchmarks) for each questionnaire. It will stop the exporter
	downloading duplicated data and remind the admin old data which suppose to be deleted remained on the server. You don't
	need to have a BenchMark.txt for the program to run. You will get an email for creating the new benchMark file.

	HEADS UP:

# Deploy and run on Server

This program will run every 5 minutes on the server. Done by martin.sh and crontab setting on server.

### What is done:

* Read and write data
* Error alert
* Error logs
* Normal running logs
* Added where to skip Error
* Save the raw data
* Deleting the raw data
* Write up the bash code to automatically run export.py regulary.
* Write a Recovery program to recover data from raw data files.



Note to myself:
    LOG_CFG=my_logging.yaml python my_server.py
