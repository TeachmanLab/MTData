# PIExporter

A python application that drag data to server and secue them automatically


## Getting Started

Create a virtual environment with python 2.7, and install dependencies
(see http://docs.python-guide.org/en/latest/dev/virtualenvs/) 
```bash
    $ virtualenv venv           
    $ source venv/bin/activate
    $ pip install -r requirements.txt
```


## Basic Overview

What this little application is going to do:

1\ Read in a data package (let's say, d).

2\ One by one, read out the data form names(scale names) in d, and then:

A\ Check if there is a file named [form_name]_[date].csv in the Active Data Pool, if not, create one

B\ Open [form_name]_[date].csv, append the data we have into it, one by one. 

C\ Keep the raw data, and then send back delete commend one by one?

D\ Close file, Log down the action and output to log.txt. If there is an error, email me.


What is done:

    Read and write data

    Error alert

    Error logs

    Normal running logs

    

What needed to be done:

    1\ Save the raw data

    3\ Add where to skip error

    4\ Deleting the raw data - Done but not yet tested

    5\ Double check on the data collecting part

    6\ Add data writing testing and error notification


