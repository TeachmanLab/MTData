import requests # To make REST requests of the client.
import time
import os.path
import rsa # To decrypt values.
import csv # To write the data into CSV file safely
import binascii
import logging
import logging.config
import yaml
import pickle
import glob
import os
from cliff.command import Command
import json
import pandas as pd
from tools import takeOrder
from tools import safeRequest
from tabulate import tabulate
# ------------------------------------------#
# Load the Configuration file
SERVER_CONFIG = 'config/server.config'

# Code needed to be added here to create a completed list of scales should have:
# Code needed to be added here for checking one participant
class Checker(object):
    """docstring for ."""
    def __init__(self, standard):
        super(, self).__init__()
        self.standard = standard
    def correct_number(self,entry):

        return number

    def completed_list(self):

        return comList




# Actually functions:
def scaleScan(config):
    log = logging.getLogger(__name__)
    log.info('Data checking started.')
    # Download Standard Scale Sheet
    sss_url = config[SERVER] + '/sss'
    sss = safeRequest(sss_url,config)
    d = Checker(sss)
    # Create checking table
    result = pd.DataFrame(index = d.completed_list(sss), columns = ['data_found','entries_in_log','entries_in_dataset','missing_rate'])
    newest = max(glob.iglob(config["PATH"]+'active_data/TaskLog'+'*.csv'), key=os.path.getctime)
    taskLog = pd.read_csv(newest)
    # Check if data exists for scale
    for scale in comList:
        filename = config[PATH]+'active_data/'+scale+'*.csv'
        if os.path.isfile(filename):
            result[scale].data_found = True
            result[scale].entries_in_log = a = len(taskLog[taskLog.task_name == scale])
            scale_data = pd.read_csv(max(glob.iglob(filename), key=os.path.getctime))
            result[scale].entries_in_dataset = b = len(scale_data)
            result[scale].missing_rate = 1 - float(b)/float(a)
        else:
            result[scale].data_found = False
    print tabulate(result, headers='keys',tablefmt='psql')
    return result



def clientScan(config):
    log = logging.getLogger(__name__)
    log.info('Data checking started.')
    # Download Standard Scale Sheet
    sss_url = config[SERVER] + '/sss'
    sss = safeRequest(sss_url,config)
    d = Checker(sss)
    # Create a table with the last task of each participant
    newest = max(glob.iglob(config["PATH"]+'active_data/TaskLog'+'*.csv'), key=os.path.getctime)
    table = pd.read_csv(newest)
    date = pd.to_datetime(table.datetime)
    table['datetime_CR'] = date
    idx = table.groupby(['participantdao_id'])['datetime_CR'].transform(max) == table['datetime_CR']
    check_tb = table[idx].sort(['participantdao_id'])
    result = check_tb[['participantdao_id','session_name','task_name']]
    # Get checking information
    result['target_task_no'] = result.apply(d.correct_number,axis=1)
    result['logged_task_no'] = result.apply(lambda entry:len(table[table.participantdao_id == entry['participantdao_id']]), axis = 1)
    result['Missing_no'] = result.apply(lambda entry:entry['target_task_no']-entry['logged_task_no'], axis=1)
    print('Number of participants finished as least a task: %s. \n',str(len(result)))
    print tabulate(result. headers='keys',tablefmt='psql')
    return result



# Entrance functions:
def scaleReport(serverName,task_list):
    log = logging.getLogger(__name__)
    try:
        takeOrder(scaleScan,serverName,task_list)
    except:


def clientReport(serverName,task_list):
    log = logging.getLogger(__name__)
    try:
        takeOrder(clientScan,serverName,task_list)
    except:



class Report(Command):
    "A simple command that report basic static for missing data."

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Report, self).get_parser(prog_name)
        subparser = parser.add_subparsers(help='sub-command help')

        # add a subcommand
        parser_a = subparser.add_parser('scale', help='scale help')
        parser_a.add_argument('serverName', nargs='?', default='.', type=str, help='serverName help')
        parser_a.set_defaults(func=scaleReport)


        # add another subcommand
        parser_b = subparser.add_parser('client', help='client help')
        parser_b.add_argument('serverName', nargs='?', default='.', type=str, help='serverName help')
        parser_b.set_defaults(func=clientReport)

        return parser

    def take_action(self, parsed_args):
        self.log.info('sending greeting')
        self.log.debug('debugging')
        parsed_args.func(parsed_args.serverName, SERVER_CONFIG)


class Error(Command):
    "Always raises an error"

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.info('causing error')
        raise RuntimeError('this is the expected exception')
