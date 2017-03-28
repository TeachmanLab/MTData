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
from tabulate import tabulate

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
        sess_name=[];
        sess2task={};
        wount=0;
        pount=0;
        for sess in data_sess:
            task_name=[];
            sess_name.append(sess['name']);
            wount=wount+pount+1;
            pount=0;
            for task_id in sess['tasks']:
                pount=pount+1;
                task_name.append(task_id['name']);
            en_task_name=list(enumerate(task_name,start=wount));
            sess2task[sess['name']]=en_task_name;

        #print sess2task;#check_dict[k['name']]=sess2task;
        return sess2task;
# describe the functions

    def correct_number(self, entry):
        #print entry['participant_id'];
        log = logging.getLogger(__name__)
        log.info("Lanched in correct_number function.")
        check_diction=self.json_dict()
        #created check_diction
        log.info("Check_diction ready.")

        if ((pd.isnull(entry['current_session'])) or (pd.isnull(entry["current_task"]))):
            log.info("Can't find task log for participant: id = %s",str(entry['participant_id']))
        elif(entry['current_session']=='COMPLETE'):
            #because completed is an empty session;
            return 38;
        else:
            number=[stask[0] for stask in check_diction[str(entry['current_session'])] if stask[1]==str(entry['current_task'])];
            #print number;
            #print entry['participant_id'];
            if (str(entry['tag'])=='post'):
                #print entry['participant_id'];
                #print "ok"
                return number[1]-1;
            else:
                #print entry['participant_id'];
                #print "ok"
                return number[0]-1;
        log.info('Cannot find record, return -999.')
        return -999




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
    print tabulate(result, headers='keys',tablefmt='psql')

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

    #counting tasks finished in TaskLog
    table=pd.DataFrame(task_data.json());
    date = pd.to_datetime(table.dateCompleted);

    table['datetime_CR'] = date;
    task_count=table.groupby(['participantId'], sort=True)['datetime_CR'].count()
    task_count = pd.DataFrame(task_count).reset_index()
    task_count.rename(columns={'participantId':'participant_id'}, inplace=True);
    task_count.rename(columns={'datetime_CR':'task_no'}, inplace=True);

    log.info("Task count table created.")
    # get status of current task
    pi=[];
    cs=[];
    ct=[];
    adm=[];
    tg=[];
    for k in pat_data.json():
        pi.append(k['id']);
        adm.append(k['admin']);
        cs.append(k['study']['currentSession']['name']);
        ct.append(k['study']['currentSession']['currentTask']['name']);
        tg.append(k['study']['currentSession']['currentTask']['tag']);
    log.info("Content filled.")
    current_status = pd.DataFrame(
        {
         'participant_id':pi,
         'current_session': cs,
         'current_task': ct,
         'admin':adm,
         'tag':tg
        })
    log.info("Current Task Status Table created.")
    current_status = current_status.merge(task_count,on='participant_id',how='outer');
    result=current_status;

    result.fillna(0);

    log.info("Tables Are Merged.")
    # Get checking information
    result['target_task_no'] = result.apply(lambda entry:d.correct_number(entry),axis=1)
    log.info("Checking completed.")
    #result['logged_task_no'] = result.apply(lambda entry:len(table[table.participantdao_id == entry['participant_id']]), axis = 1)
    result['Missing_no'] = result.apply(lambda entry:entry['target_task_no']-entry['task_no'], axis=1)

    log.info('Number of participants finished as least a task: %s. \n',str(len(result)))
    #print tabulate(result, headers='keys',tablefmt='psql')
    #result.to_csv('/Users/any/Desktop/testing data/reports/client_report_3.18.csv')
    if not os.path.exists(config["PATH"] + 'report/'):
        os.makedirs(config["PATH"] + 'report/')
    result.to_csv(config["PATH"] + 'report/' + 'client_report' + '_' + time.strftime(config["DATE_FORMAT"] + '_' + time.strftime(config["TIME_FORMAT"]) +'.csv'))
    #df = pd.read_csv('/Users/any/Desktop/testing data/reports/client_report_3.18.csv');
    #df.fillna(0);
    #print df
    print tabulate(result,headers=['participant_id','admin','current_session','current_task','tag','task_no','target_task_no','Missing_no'],tablefmt='psql');
    print 'data saved'
    return result;



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
