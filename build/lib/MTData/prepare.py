import requests # To make REST requests of the client.
import time
import os.path
import csv
import binascii
import logging
import logging.config
import yaml
import json
from cliff.command import Command
from tools import safeRequest
from scales import *
from clean_dup import clean_dup
from scores import scores
from transform import transform
import pandas as pd
from pandas import Series, DataFrame
import numpy as np
from tabulate import tabulate
import glob
import rsa # To decrypt values.
import pickle
import os

SERVER_CONFIG = 'config/server.config'




def prepare(scaleName,scalePath,state):
    log = logging.getLogger('prepare')
    #scale_df=pd.read_csv(scalePath);
    #obj=eval(scaleName)(scale_df,'raw');
    #def scores(scaleName,scalePath):
    clean_dup(scaleName,scalePath,state);
    scores(scaleName,scalePath,state);
    transform(scaleName,scalePath,state);



def read_servername(SERVER_CONFIG,scaleName,scalePath):
    log = logging.getLogger('read_server')
    try:
        address = yaml.load(open(SERVER_CONFIG, 'r'))
        log.info('Address book read successfully.')
    except:
        log.critical('Address book read failed. Emailed admin.', exc_info=1)
    if (scalePath in address.keys()):
        config = address[scalePath]
        log.info('Address for export: %s. Ready?: %s',str(scalePath),str(config['READY']))
        if config['READY']:
            print config
            return config
    else:
        log.info("severname is wrong")
        return None;

def read_scalename(SERVER_CONFIG,scaleName,scalePath):
    if scaleName == "all":
        config=read_servername(SERVER_CONFIG,scaleName,scalePath);
        filename=(config["PATH"]+'testing_data/bbmark.json');
        #print filename
        with open (filename) as f:
            data=f.read();
        dic=json.loads(data);
        print("read BechMark ok!")
        for sname in dic.keys():
            print sname
            fileList = sorted(glob.glob(config["PATH"]+'testing_data/'+sname+'*.csv'))
            try:
                newest = max(glob.iglob(config["PATH"]+'testing_data/'+sname+'*.csv'), key=os.path.getctime)
            except:
                print sname+" files do not exit"
            else:
                prepare(sname,newest,True);
    else:
        prepare(scaleName,scalePath,True);



class Prepare(Command):
    "Command for exporting data from servers."

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Prepare, self).get_parser(prog_name)
        parser.add_argument('scaleName', nargs='?', default='.')
        parser.add_argument('scalePath', nargs='?', default='.')
        return parser

    def take_action(self, parsed_args):
        self.log.info('sending greeting')
        self.log.debug('debugging')
        read_scalename(SERVER_CONFIG,parsed_args.scaleName,parsed_args.scalePath);

class Error(Command):
    "Always raises an error"

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.info('causing error')
        raise RuntimeError('this is the expected exception')
