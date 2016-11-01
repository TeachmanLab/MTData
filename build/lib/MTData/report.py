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
def completed_list(sss):

# Actually functions:
def scaleScan(config):
    log = logging.getLogger(__name__)
    log.info('Data checking started.')
    # Download Standard Scale Sheet
    sss_url = config[SERVER] + '/sss'
    sss = safeRequest(sss_url,config)
    # Create checking table
    comList = completed_list(sss)
    result = pd.DataFrame(index = comList, columns = ['data_found','entries_in_log','entries_in_dataset','missing_rate'])
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
