# This is the function for combining all the data files for one(or All) scales.
# It takes two argument, name of scales and destination.
# If name = all, combine all the scales in the destination folders.
# The function will return as Scale Object. If name = all, it will return a list(or dict) of objects.
import os
import pandas as pd
import json
import datetime
import requests # To make REST requests of the client.
import time
import os.path
import binascii
import logging
import logging.config
import yaml
import json
from cliff.command import Command

# function used to do combine multiple csv files into one:
def combine(scaleList,path):
    if not os.path.exists(path+'/master/'):
        os.makedirs(path+'/master/')
    if scaleList == 'All':
        benchMarkFile = open(path +'/benchMark.json').read()
        scaleList = json.loads(benchMarkFile).keys()
        for scale in scaleList:
            combine(scale,path)
        return("All are done!")
    else:
        fileList = [filename for filename in os.listdir(path) if filename.startswith(scaleList)]
        dataset = pd.DataFrame({'A' : []})
        for files in fileList:
            if dataset.empty:
                dataset = pd.read_csv(path+'/'+files)
                print dataset
            else:
                temp_dataset = pd.read_csv(path+'/'+files)
                dataset = pd.concat([dataset,temp_dataset],ignore_index=True)
                print dataset
        dataset.to_csv(path+'/master/'+scaleList+'_'+datetime.datetime.now().strftime("%Y-%m-%d")+'_master.csv')
        return dataset

# Function used by report, export, and decode for requests data from server.
def safeRequest(url, config):
    log = logging.getLogger(__name__)
    log.info("Trying to Request data for %s ......", url)
    try:
        response = requests.get(url, auth=(config["USER"],config["PASS"]))
        m = response.raise_for_status()
        log.info("Data request successfully, see below for request detail:\n%s\nIssues: %s", url, str(m)) # Log successful data request
        if response != None:
            try:
                data = response.json()
                log.info("We got something new! Let's have a closer look!")
                return response
            except:
                log.critical("Server: %s. Can't read data in json form. Did not receive a json response, perhaps log-in credentials are incorrect? See below for error information:\n", url, exc_info = 1)
    except requests.exceptions.Timeout:
        log.critical("Data request timed out for url: " + url + ". See below for error information:\n", exc_info = 1)
    except requests.exceptions.TooManyRedirects:
        log.critical("Too many redirects for url: " + url + ". See below for error information:\n", exc_info = 1)
    except requests.exceptions.RequestException as e:  # DF: We may loose some detail here, better to check all exceptions.
        log.critical("Server: %s. Data request failed, fatal, emailed admin. Error was " + str(e) + " see below for error information:\n", config['SERVER'], exc_info = 1)


# Functions used to take order:
def takeOrder(action,serverName,task_list):
    log = logging.getLogger(__name__)
    try:
        address = yaml.load(open(task_list, 'r'))
        log.info('Address book read successfully.')
    except:
        log.critical('Address book read failed. Emailed admin.', exc_info=1)
    if serverName == '.':
        for key in address:
            config = address[key]
            log.info('Server for missing data report: %s. Ready?: %s',str(key),str(config['READY']))
            if config['READY']: action(config)
    elif (serverName in address.keys()):
        config = address[serverName]
        log.info('Server for missing data report: %s. Ready?: %s(Ready Checked is overwrited).',str(serverName),str(config['READY']))
        action(config)
    else:
        log.info("Server name is not correct, please check.")
