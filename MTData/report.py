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
import numpy as np
from tools import takeOrder
from tools import safeRequest
from pandas.io.json import json_normalize

#from tabulate import tabulate
# ------------------------------------------#

import numpy as np;
from pandas import Series, DataFrame;
# Load the Configuration file
SERVER_CONFIG = 'config/server.config'

# Code needed to be added here to create a completed list of scales should have:
# Code needed to be added here for checking one participant
class Checker(object):
    def __init__(self, standard):
        super(Checker, self).__init__()
        self.standard = standard.json()

    def json_dict(self):
        log = logging.getLogger(__name__)
        d=self.standard;
        data_seg=d[0];
        data_sess=data_seg['sessions'];
        #keyname=[];
        #check_dict={};
        #for k in d:
            #keyname.append(k['name']);
            #data_sess=k['sessions'];
        sess_name=[];
        sess2task={};
        wount=0;
        pount=1;
        for sess in data_sess:
            task_name=[];
            sess_name.append(sess['name']);
            wount=pount;
            for task_id in sess['tasks']:
                pount=pount+1;
                task_name.append(task_id['name']);
            en_task_name=list(enumerate(task_name,start=wount));
            sess2task[sess['name']]=en_task_name;
        #check_dict[k['name']]=sess2task;
        return sess2task;

    """docstring for ."""
    '''
    this is a function that transfer the json file into a list of dictionaries
    '''
    def correct_number(self, entry):
        log = logging.getLogger(__name__)
        log.info("Lanched in correct_number function.")
        check_diction=self.json_dict()
        print (type(check_diction) is dict)
        print check_diction
        log.info("Check_diction ready.")
        print entry['current_session']
        print entry['current_task']
        #print check_diction[str(entry['current_session'])]
        if ((pd.isnull(entry['current_session'])) or (pd.isnull(entry["current_task"]))):
            log.info("Can't find task log for participant: id = %s",str(entry['participant_id']))
        else:
            for stask in check_diction[str(entry['current_session'])]:
                log.info("Let's find out the number!")
                if stask[1]==str(entry['current_task']):
                    number=stask[0];
                    log.info("Number got!")
                    return number-1
        log.info('Cannot find record, return -1.')
        return -1




    def completed_list(self):
        comList = []

        for study in self.standard:
            for session in study['sessions']:
                for task in session['tasks']:
                    if task['name'] not in comList:
                        comList.append(task['name'])

        return comList




# Actually functions:
def scaleScan(config):
    log = logging.getLogger(__name__)
    log.info('Data checking started.')
    # Download Standard Scale Sheet
    sss_url = config["SERVER"] + 'study'
    log.info('Successfully get server address.')
    sss = safeRequest(sss_url,config)
    log.info('Successfully read study schedule.')
    d = Checker(sss)
    # Download updated TaskLog
    log_url = config["SERVER"] + 'export/TaskLog'
    logs = safeRequest(log_url,config)
    log.info("Successfully get TaskLog information.")
    # Create checking table
    result = pd.DataFrame(index = d.completed_list(), columns = ['data_found','entries_in_log','entries_in_dataset','missing_rate'])
    log.info("Report format ready.")
    #newest = max(glob.iglob(config["PATH"]+'active_data/TaskLog'+'*.csv'), key=os.path.getctime)
    taskLog = json_normalize(logs.json())
    print taskLog
    log.info("Ready to check.")
    for scaleName in d.completed_list():
        log.info("Ready to search file %s",scaleName)
        filename = config['PATH']+'active_data/'+ scaleName +'*.csv'
        exist = False
        try:
            scale_data = pd.read_csv(max(glob.iglob(filename), key=os.path.getctime))
            exist = True
            log.info("%s data found.", str(scaleName))
        except:
            print "Data not found."
            # Check if data exists for scale
        log.info("Data retrived successfully.")
        if (exist):
                ## add JsPsychTrial  condition count the last trial in this sesstion
            result.set_value(scaleName,'data_found',True)
            a = len(taskLog[(taskLog['taskName'] == scaleName)])
            result.set_value(scaleName,'entries_in_log',a)
            log.info("Report generated.")
            if scaleName == 'JsPsychTrial':
                b = len(scale_data[scale_data.stimulus == 'final score screen'])
                result.set_value(scaleName,'entries_in_dataset',b)
            else:
                b = len(scale_data)
                result.set_value(scaleName,'entries_in_dataset',b)
            result.set_value(scaleName,'missing_rate', "{:.9f}".format(1 - float(b)/float(a)))
            log.info("Counting completed.")
        else:
            result.set_value(scaleName,'data_found',False)
            log.info("Data not found for %s",str(scaleName))
    #print tabulate(result, headers='keys',tablefmt='psql')
    print result
    return result



def clientScan(config):
    log = logging.getLogger(__name__)
    log.info('Data checking started.')
    # Download Standard Scale Sheet
    sss_url = config["SERVER"] + 'study'
    log.info('Successfully get server address.')
    sss = safeRequest(sss_url,config)
    log.info('Successfully read study schedule.')
    d = Checker(sss)
    log_url=config["SERVER"]+'export/TaskLog';
    task_data = safeRequest(log_url,config);
    pat_url = config["SERVER"] + 'export/Participant'
    pat_data=safeRequest(pat_url,config);
    log.info("Ready for checking.")
    table=pd.DataFrame(task_data.json());
    log.info("Well, just in case.")
    #table['dateCompleted']
    date = pd.to_datetime(table.dateCompleted);

    table['datetime_CR'] = date;
    task_count=table.groupby(['participantId'], sort=True)['datetime_CR'].count()
    task_count = pd.DataFrame(task_count).reset_index()
    task_count.rename(columns={'participantId':'participant_id'}, inplace=True);
    task_count.rename(columns={'datetime_CR':'task_no'}, inplace=True);
    #task_count
    log.info("Task count finished.")
    pi=[];
    cs=[];
    ct=[];
    for k in pat_data.json():
        pi.append(k['id']);
        cs.append(k['study']['currentSession']['name']);
        ct.append(k['study']['currentSession']['currentTask']['name']);
    log.info("Content filled.")
    current_status = pd.DataFrame(
        {
         'participant_id':pi,
         'current_session': cs,
         'current_task': ct
        })
    log.info("Table created.")
    current_status = current_status.merge(task_count,on='participant_id',how='outer');
    result=current_status;
    log.info("Final report created.")
    print result
    print pd.isnull(result)
    # Get checking information
    result['target_task_no'] = result.apply(lambda entry:d.correct_number(entry),axis=1)
    log.info("Checking completed.")
    #result['logged_task_no'] = result.apply(lambda entry:len(table[table.participantdao_id == entry['participant_id']]), axis = 1)
    result['Missing_no'] = result.apply(lambda entry:entry['target_task_no']-entry['task_no'], axis=1)
    log.info('Number of participants finished as least a task: %s. \n',str(len(result)))
    #print tabulate(result, headers='keys',tablefmt='psql')
    print result
    return result



# Entrance functions:
def scaleReport(serverName,task_list):
    log = logging.getLogger(__name__)
    try:
        takeOrder(scaleScan,serverName,task_list)
    except:
        print("Failed to take order.")

def clientReport(serverName,task_list):
    log = logging.getLogger(__name__)
    try:
        takeOrder(clientScan,serverName,task_list)
    except:
        print("Failed to take order.")



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
