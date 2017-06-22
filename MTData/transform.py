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
import pandas as pd
from pandas import Series, DataFrame
import numpy as np
from tabulate import tabulate
import glob
import rsa # To decrypt values.
import pickle
import os


SERVER_CONFIG = 'config/server.config'

def transform(scaleName,scalePath,state):
    print " you are in transform"
    log = logging.getLogger('tranform')
    scale_df=pd.read_csv(scalePath);
    try:
        obj=eval(scaleName)(scale_df,state);
    except:
        print "scaleName "+scaleName+" is not correct, please check"
    else:
        #print "counting scores"
        try:
            transed_obj=obj.trans();
        except:
            print "transform function is not available for "+scaleName;
        else:
            parent_path=os.path.abspath(os.path.join(scalePath, os.pardir))
            grap_path=os.path.abspath(os.path.join(parent_path, os.pardir))
    #print grap_path
            if not os.path.exists(grap_path + '/processed_data/wideform_data'):
                os.makedirs(grap_path + '/processed_data/wideform_data')
            transed_obj.to_csv(grap_path+ '/processed_data/wideform_data/' + scaleName+'_transed' + '_' + time.strftime("%b_%d_%Y" + '_' + time.strftime("%H_%M_%S") +'.csv'))
            print "transed "+scaleName+' '+"data saved"


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
        filename=(config["PATH"]+'testing_data/benchmark.json');
        #print filename
        with open (filename) as f:
            data=f.read();
        dic=json.loads(data);
        print("read BechMark ok!")
        for sname in dic.keys():
            print sname+" processed"
            fileList = sorted(glob.glob(config["PATH"]+'testing_data/test_all/'+sname+'*.csv'))
            try:
                newest = max(glob.iglob(config["PATH"]+'testing_data/test_all/'+sname+'*.csv'), key=os.path.getctime)
            except:
                print sname+" files do not exit"
            else:
                transform(sname,newest,False);
    else:
        transform(scaleName,scalePath,False)



class Trans(Command):
    "Command for exporting data from servers."

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Trans, self).get_parser(prog_name)
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
