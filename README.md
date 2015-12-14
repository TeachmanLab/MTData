# PIExporter

A python application that drag data to server and secue them automatically


## Getting Started

Create a virtual environment with python 2.7, and install dependencies
(see http://docs.python-guide.org/en/latest/dev/virtualenvs/) 
```bash
    $ virtualenv venv           
    $ source venv/bin/activate
    $ pip install -r requirements.txt
    $ cp export.config.example export.config
````

## Configuration

Copy the export.config.example file to export.config, and edit the settings so they
match your configuration needs.


## Basic Overview

What this little application is going to do:

1\ Read in a data package (oneShot).

2\ One by one, read out the data form names(scale names) in oneShot, and then:

A\ Check if there is a file named [form_name]_[date].csv in the Active Data Pool, if not, create one

B\ Open [form_name]_[date].csv, append the data we have into it, one by one. 

C\ Keep the raw data, and then send back delete commend one by one?

D\ Close file, Log down the action and output to log files. If there is an error, email admin.



## Data requesting

Data requesting is done via the requests module, basic documentation could be found here:

http://docs.python-requests.org/en/latest/



## Data writing

Data writing is doen via the csv module, basic documentation could be found here:

https://docs.python.org/2/library/csv.html#csv-fmt-params



## Logging

Logging is done via the logging module. Configuration is through log.config. ALL temple and account information should
configure via log.config. See comments for reminder.

Logging behaviors list below:

    A\ There are five level of logging information, from low to high in priority are: debug/info/warning/error/critical

    B\ All information will be stored in DEBUG.log.

    C\ All information belong to and beyond info level will be stored in Daily.log.

    D\ All information belong to and beyond warning level will be stored in error.log.

    E\ All information reach critical level will be stored in bread_down.log, and emails will be sent to admin meanwhile.

    F\ All log files will rotate at midnight. Old log files will be added suffix with local date. Log files will be
    rotating in a year long period(366 days).

Break_down situation includes:

    A\ Data request failure. Imply a network breakdown.

    B\ Data delete failure. Imply a network breakdown and post a serious data security threat.

    C\ Data writing failure. Imply a breakdown in csv module and need immediate attention.

Basic documentation about logging could be found here:

https://docs.python.org/2/library/logging.html



## Decrypting

    Original module. Need more documentation here:



## Backup system:

    Data backup is done via shelve module.

    A\ All new data package(quest within any oneShot) will be stored in
    raw_data/[scaleName]_[Date].raw.db before they are decrypted and recorded into active_data/[scaleName]_[Date].csv.

    B\ Raw data will be stored as Objects, and could be reversed into Objects via shelve.

    C\ Keys for backup data are in form of [[scaleName] + '_' + TIME].

    D\ Backup data files is consistent with active data file in name and will be created in a daily base.

    HEAD UP: Creating new raw data files will not be logged into log files, but creating new active data files will.

Basic documentation about shelve:

https://docs.python.org/2/library/shelve.html


# Data deleting:

    Just so you know, turn on Delete mode by setting constant DELETE_MODE to True. (Highly NOT recommended in testing
    phrase.)

What is done:

    Read and write data

    Error alert

    Error logs

    Normal running logs

    Added where to skip error

    Save the raw data

    Deleting the raw data - Done but not yet tested


What needed to be done:

    5\ Double check on the data collecting part

    6\ Write a Recovery program to recover data from raw data files.


Note to myself:
    LOG_CFG=my_logging.yaml python my_server.py





