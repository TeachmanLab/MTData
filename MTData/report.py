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

import numpy as np;
from pandas import Series, DataFrame;
# Load the Configuration file
SERVER_CONFIG = 'config/server.config'

# Code needed to be added here to create a completed list of scales should have:
# Code needed to be added here for checking one participant
class Checker(object):

    def __init__(self, standard):
        super(, self).__init__()
        self.standard = standard.json()




    def json_dict(self):
       d=self.standard;
       data_seg=d[0];
       data_sess=data_seg['session'];
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
'''
    def json_dict(self):



        #with open (filename) as f:
            #data=f.read();
        #d=json.loads(data);
       d=self.standard;
        keyname=[];
        check_dict={};
        for k in d:
            keyname.append(k['name']);
            data_sess=k['sessions'];
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
            check_dict[k['name']]=sess2task;
        return check_dict;
'''
    def correct_number(self，entry):
        check_diction＝self.json_dict()
        for stask in check_diction[entry['session_name']]:
            if stask[1]==entry['task_name']:
                number=stask[0];
            #elsete
            '''
            warning message? error report?
            '''


        return number

'''
        def checker(sname,tname):
    se_list=sess2task[sname];
    #print se_list;
    for stask in se_list:
        if stask[1]==tname:
            numbb=stask[0];
            #print numbb
    return numbb
'''




    def completed_list(self):
        comList = []

        for study in self.standard:
            for session in study['sessions']:
                for task in session['tasks']:
                    if task['name'] not in comList:
                        comList.append(task['name'])

        return comList




# Actually functions:

# scaleScan detect whether a scale or task is missing in the actual testing schedule
# it will also report entries numbers in tasklong and entries numbers in dataset.
# and calculate the missing rate for you.
def scaleScan(config):
    log = logging.getLogger(__name__)
    log.info('Data checking started.')
    # Download Standard Scale Sheet
    sss_url = config[SERVER] + '/api/export/schedule'
    sss = safeRequest(sss_url,config)
    d = Checker(sss)
    # Create checking table
    result = pd.DataFrame(index = d.completed_list(), columns = ['data_found','entries_in_log','entries_in_dataset','missing_rate'])
    newest = max(glob.iglob(config["PATH"]+'active_data/TaskLog'+'*.csv'), key=os.path.getctime)
    taskLog = pd.read_csv(newest)
    # Check if data exists for scale

    ## add JsPsychTrial  condition count the last trial in this sesstion

    for scale in comList:
        #if

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


# clientScan will check missing data for individual participants.
# It will list the last session/task, planned task number and logged task number for you,
# and calculate the missing rate.
def clientScan(config):
    log = logging.getLogger(__name__)
    log.info('Data checking started.')
    # Download Standard Scale Sheet
    sss_url = config[SERVER] + '/api/export/schedule'
    sss = safeRequest(sss_url,config)
    d = Checker(sss)
    # Create a table with the last task of each participant
    newest = max(glob.iglob(config["PATH"]+'active_data/TaskLog'+'*.csv'), key=os.path.getctime)
    newest_client = max(glob.iglob(config["PATH"]+'active_data/Participant'+'*.csv'), key=os.path.getctime)
    table_client = pd.read_csv(newest_client)

    task_url=sss_url = config[SERVER] + '/api/study'


    #table = pd.read_csv(newest)
    #date = pd.to_datetime(table.datetime)
    #table['datetime_CR'] = date
'''
### participant : current status from json;

    with open("Participant.json","r") as f:
        data = f.read()
    d = json.loads(data)
    pp=d
    pi=[];
    cs=[];
    ct=[];
    for k in d:

        pi.append(k['id']);
        cs.append(k['study']['currentSession']['name']);
        ct.append(k['study']['currentSession']['currentTask']['name']);
        #current_status = pd.DataFrame({'current_sesstion': cs,'current_task': ct},index=pi);
        current_status = pd.DataFrame(
    {
        'participant_id':pi,
     'current_sesstion': cs,
     'current_task': ct
    })


'''
'''
    ###participant: current status from csv
    current_status=table_client[['id','session_name','task_name']] # not sure about the names


'''

'''
    ### tasklog from csv;

    date = pd.to_datetime(table.date_completed)
    table['datetime_CR'] = date;
    task_count=tb.groupby(['participantdao_id'], sort=True)['datetime_CR'].count()

    task_count = pd.DataFrame(task_count).reset_index()
    task_count.rename(columns={'participantdao_id':'participant_id'}, inplace=True);
    task_count.rename(columns={'datetime_CR':'task_no'}, inplace=True);

    current_status = current_status.merge(task_count,on='participant_id',how='outer')

'''


    result=current_status;


    '''
    this is from diheng
    idx = table.groupby(['participantdao_id'])['datetime_CR'].transform(max) == table['datetime_CR']
    check_tb = table[idx].sort(['participantdao_id'])
    study_info = table_client[['id','study','cbmCondition']]
    study_info.rename(columns={'id':'participant_id'}, inplace=True)
    result = check_tb[['participantdao_id','session_name','task_name']]
    result.rename(columns={'participantdao_id':'participant_id'}, inplace=True)
    result = result.merge(study_info,on='participant_id',how='outer')
'''




    # Get checking information
    # Anyi, please change the line below:
    # Go over all the participants, find out the expected number of tasks:
    result['target_task_no'] = result.apply(lambda entry:d.correct_number(entry),axis=1)

    # Check the actual number of task belongs to a participant
    result['logged_task_no'] = result.apply(lambda entry:len(table[table.participantdao_id == entry['participant_id']]), axis = 1)
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




############

''' for the lambda ? it is defauted seted to be row wise , so we need to set axis=1 at the edn.
