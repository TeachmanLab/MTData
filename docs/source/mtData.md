About MindTrails Data
======

A command-line tool that handle data exporting, decrypting and basic checking for
mindtrails or mindtrails-like website. Support multiple websites data collecting. It also contains toolbox for data analysis.

Environment Note:
For Mac Users:
Please update Xcode version to ensure successful update.

Basic idea
---------

The main idea of MTData is three-fold:
1. ```export``` encrypted data as json files
2. ```decode``` json files locally into csv files
3. ```report``` basic missing data measurements based on the decrypted csv files

At the end of the day you will have raw backup json data and ready-to-use csv format data for your analysis. You also can refer to automatically generated reports and logs for data integrity issues.


Examples
---------

```sh
# download and delete all the deleteable questionnaire entries on multiple servers
$ MTData export . .

# or

$ MTData export

# download all the questionnaire entries that should not be deleted from the templeton server.
$ MTData export templeton static

# decode all the questionnaire for mindtrails server.
$ MTData decode mindtrails .

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

Create a virtual environment with python 2.7.12+, and install dependencies
(see http://docs.python-guide.org/en/latest/dev/virtualenvs/)
```bash
    $ virtualenv venv           
    $ source venv/bin/activate
    $ pip install requirements.txt
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

Edit the server.config, log.config and recover_log.config.

*Warning* Failed to setup the config files will probably lead to unexpected errors. For example, MTData might return a very confusing error "export is not a MTData command, do you mean?..." It will disappear after you correctly config all three config files.


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
You can override READY:False in ```report``` and ```decode``` by specifying the name of server, but you *CANNOT* ```export``` a server's data if READY is False at any time.

**Note for 'deleteable'**
In MindTrails, all tables have a 'deleteable' attribute. 'deleteable' is True when this table contains sensitive data that you don't want to keep on your front end server, and therefore requires to be downloaded and deleted frequently (like, every 5 minutes). 'deleteable' is False when this table is needed for the online study constantly (like, baseline score for alarming, task logs needed for reference).

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




Current Usage
===========

export
---------

  ```sh
  $ MTData export [serverName, default=.(All)] [scaleName =./static/All]

  ```

decode
--------

  ```sh
  $ MTData decode [serverName, default=.(All)] [scaleName, default=.(All)]
  ```

report
----------

  ```sh
  $ MTData report client [serverName, default=.(All)]
  $ MTData report scale [serverName, default=.(All)]
  ```

tools
---------




TODO
=========
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

What is done
=========
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
