# ------------------------------------------#
# Import the Requests

import requests # To make REST requests of the client.
import time
import os.path
import binascii
import logging
import logging.config
import yaml
import json
from cliff.command import Command
from tools import safeRequest


# ------------------------------------------#


# Empty Global variables created here:

# Load the Configuration file
SERVER_CONFIG = 'config/server.config'
print 'helloa'
# Set up logging config files
# Setting up files directories and logging config files
# if not os.path.exists("/Users/dz8t/Box Sync/logs/"): # Can't find a better way to do this......
#    os.makedirs("/Users/dz8t/Box Sync/logs/")
logging.config.dictConfig(yaml.load(open('config/log.config', 'r')))

print 'hellob'



# ------------------------------------------#

def safeKeep(scaleName, response, file, config):
    log = logging.getLogger('export.safeKeep')
    stamp = time.strftime(config["TIME_FORMAT"])
    try:
        with open(file, 'a') as dataJson:
           dataJson.write(response.text.encode('utf-8'))
           log.info(scaleName + " data backup successfully.")
        return True
    except:
        log.critical(scaleName + ' data backup failed, immediate attention needed.\n', exc_info = 1)
        return False

print 'hellob'
# DF: Should likely write our own method that will make the request and return
# a json response, since things can go wrong here in lots of ways and we want
# to try and catch all of them. In this way we can handle exceptions, emailing
# us in the event of an error. THIS CODE IS NOT COMPLETE. I'm just roughly
# trying to show what it should do.



# SafeDelete function, use this to delete data entries and log down system message
def safeDelete(url, config):
    log = logging.getLogger('export.safeDelete')
    log.info("Trying to Delete data for %s ......", url)
    try:
        # DH: Make request, delete and check the status code of the response.
        delete = requests.delete(url, auth=(config["USER"],config["PASS"]))
        m = delete.raise_for_status()
        log.info("Data delete successfully, see below for request detail:\n%s\nIssues: %s", url, str(m)) # Log successful data delete
        return True
    except requests.exceptions.RequestException as e:  # DF: We may loose some detail here, better to check all exceptions.
        log.critical("Server: %s. Data delete failed, fatal, emailed admin. see below for error information:\n", config['SERVER'], exc_info = 1)
        return False

print 'helloc'
# SafeWrite function, use this to write questionnaire data into csv files
def safeSave(response, ks, scaleName, deleteable, config):
    #A\ Check if there is a file named [form_name]_[date].csv in the Active Data Pool, if not, create one
    raw_file = config["PATH"] + 'raw_data/' + scaleName + '_' + time.strftime(config["DATE_FORMAT"] + '_' + time.strftime(config["TIME_FORMAT"]) +'.json')
#B\ Save the raw json files:
    log = logging.getLogger('export.safeSave')
    backup = safeKeep(scaleName, response, raw_file, config)
    d = 0
    error = 0
    quest = response.json()
    benchMark = {}
# Read in benchMark information
    try:
        with open(config["PATH"]+'active_data/benchMark.json',"rb") as benchMarkJson:
            benchMark = json.load(benchMarkJson)
        log.info("benchMark information successfully retrived.")
    except:
        log.info("benchMark information retrived failed, immediate attention needed. Detail:\n", exc_info = 1)
    if scaleName in benchMark.keys():
        log.info("benchMark found for %s", scaleName)
    else:
        benchMark[scaleName] = {}
        benchMark[scaleName]['current'] = 0 # Set benchMark for this scale
        benchMark[scaleName]['deleteable'] = deleteable # Set benchMark for this scale
        log.info("New benchMark created for %s", scaleName)
    newBenchMark = benchMark[scaleName]['current']

    if deleteable:
        for entry in quest:
            if int(entry['id']) > benchMark[scaleName]['current']: # Check if entries are new comparing to last request
                if newBenchMark < int(entry['id']): newBenchMark = int(entry['id']) # Record the lastes ID within current request
                try:
                    if backup and config["DELETE_MODE"]:                              # If the scale is backed-up, delete the entry after it is successfully recorded.
                        if safeDelete(config["SERVER"] + 'export/' + scaleName + '/' + str(entry['id']), config): d += 1 # If deleting success, d increase.
                    else: log.info('Questionnaire - %s, ID - %s, data cleaning on hold. Detail: Backup: %s, Delete Mode: %s', scaleName, str(entry['id']), str(backup), str(config["DELETE_MODE"]))
                except:
                    error += 1
                    log.critical("Failed in saving entry, Questionnaire: %s, Entry ID: %s", scaleName, str(entry['id']), exc_info = 1)
            else:
                log.info('Questionnaire - %s, ID - %s, data writing skipped. Reason: Not a new entry.', scaleName, str(entry['id']))
                log.critical('Warning: Previous sensitive data is found on server, please delete it ASAP. Detail: Questionnaire - %s, ID - %s. ', scaleName, str(entry['id'])) #
    else:
        log.info("Non-deleteable data downloaded. Please make sure you only decode the most recent copy.")
    log.info("Questionnaire %s data cleaning finished - %s new entries successfully deleted on MindTrails.", scaleName, str(d))
    if newBenchMark > benchMark[scaleName]['current']: benchMark[scaleName]['current'] = newBenchMark # Update the lastest ID after all the new data writing
    if error > 0:
        log.critical("Questionnaire %s update error - %s new entries failed to save.", scaleName, str(error))

    try:
        with open(config["PATH"]+'active_data/benchMark.json',"wb") as benchMarkJson:
            json.dump(benchMark,benchMarkJson)
        log.info("benchMark information update successfully.")
    except:
        log.warning("benchMark information update failed, duplicated record may created, please check:\n", exc_info = 1)

# Sub function within safeExport:
def safeCollect(scale,config):
    log = logging.getLogger(__name__)
    s = 0
    response = safeRequest(config["SERVER"]+'export/'+scale['name'], config)
    if response!= None:
        quest = response.json()
        if quest != None:
            if scale['size'] != 0:
                ks = list(quest[0].keys())
                ks.sort()
                log.info("Questionnaire %s updated - %s new entries received.", str(scale['name']), str(scale['size']))
                safeSave(response, ks, str(scale['name']), scale['deleteable'], config) # Safely write the whoe questionnaire into the data file
                s += 1
            else: log.info("No new entries found in %s", str(scale['name']))
        else:
            log.warning("""This is weired... It seems that there is nothing out there or I am blocked from MindTrails. You might already get an email from me
            reporting some network issues. Be alerted, stay tuned. Server: %s""", config['SERVER'])
    return s



# Main function, use this to read and save questionnaire data
def safeExport(data,scaleName,config):
# One by one, read out the data form names(scale names) in d, and then:
    log = logging.getLogger('export.safeExport')
    log.info("Database update in progress......")
    s = 0
    if scaleName == '.':
        for scale in data:
            # Only download deleteable scales:
            if scale['deleteable']:
                s = safeCollect(scale,config)
            else:
                log.info("Questionnaire %s is not deleteable. It will be downloaded at the end of the day by another robot.", str(scale['name']))

    elif scaleName == 'all':
        for scale in data:
            # Only download deleteable scales:
            s = safeCollect(scale,config)

    elif scaleName == 'static':
        for scale in data:
            # Only download deleteable scales:
            if not scale['deleteable']:
                s = safeCollect(scale,config)

    else:
        n = 0
        for scale in data:
            if scale['name'] == scaleName:
                s = safeCollect(scale,config)
                log.info("Scale %s is found and data are collected.", scaleName)
                n += 1
        if n == 0:
            log.info("Scale name is not correct, please check.")

    log.info("Database update finished: %s questionnaires' data updated.", str(s))


def pathCheck(config):
    log = logging.getLogger('export.pathCheck')
    try:
        if not os.path.exists(config["PATH"]+"raw_data/"):
            os.makedirs(config["PATH"]+"raw_data/")
            log.info("Successfully created raw_data folder.")
        if not os.path.exists(config["PATH"]+"active_data/"):
            os.makedirs(config["PATH"]+"active_data/")
            log.info("Successfully created active_data folder.")
    except:
        log.critical("Server: %s. Failed to create data or log files, fatal, emailed admin.", config['SERVER'], exc_info=1)

# ------------------------------------------#
# This is the main module
def export(scaleName,config):
    log = logging.getLogger('martin')
    log.info("""Hi PACT Lab, this is faithful android Martin from Laura\'s server. Everything is alright here, and seems to be
     a good time for a hunt. I am going out for a regular check and will come back soon. Don't miss me PACT Lab, it wouldn't
     take too long.""")
    pathCheck(config) #Check storage path
    log.info(" (Martin is out for hunting data......) ")

    oneShot = safeRequest(config['SERVER']+"export/", config)

    if oneShot != None:
        log.info("""Alright I am back! Pretty fruitful. Seem like it is going to be comfortable for a little while. Alright,
     I am heading to the server for a little rest, will talk to you guys in PACT Lab in a little while. -- Martin""")
        if (oneShot.json() != None): safeExport(oneShot.json(),scaleName,config)
    else:
        log.warning("""This is weired... It seems that there is nothing out there or I am blocked from MindTrails. You might already get an email from me
     reporting some network issues. Be alerted, stay tuned. Server: %s.""",config['SERVER'])
    log.info("I am tired and I am going back to Laura's server for a rest. See you later!")

# This is a over all program
def martin(task_list,serverName,scaleName):
    log = logging.getLogger('martin')
    try:
        address = yaml.load(open(task_list, 'r'))
        log.info('Address book read successfully.')
    except:
        log.critical('Address book read failed. Emailed admin.', exc_info=1)
    if serverName == '.':
        for key in address:
            config = address[key]
            log.info('Address for export: %s. Ready?: %s',str(key),str(config['READY']))
            if config['READY']: export(scaleName,config)
    elif (serverName in address.keys()):
        config = address[serverName]
        log.info('Address for export: %s. Ready?: %s',str(serverName),str(config['READY']))
        if config['READY']: export(scaleName,config)
    else:
        log.info("Server name is not correct, please check.")


# Works here:

# Make it a command line:
class Export(Command):
    "Command for exporting data from servers."

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Export, self).get_parser(prog_name)
        parser.add_argument('serverName', nargs='?', default='.')
        parser.add_argument('scaleName', nargs='?', default='.')
        return parser

    def take_action(self, parsed_args):
        self.log.info('sending greeting')
        self.log.debug('debugging')
        martin(SERVER_CONFIG,parsed_args.serverName,parsed_args.scaleName)

class Error(Command):
    "Always raises an error"

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.info('causing error')
        raise RuntimeError('this is the expected exception')
