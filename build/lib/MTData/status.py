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
from scales import *
import pandas as pd
from pandas import Series, DataFrame
import numpy as np
from tabulate import tabulate


def aloha(scaleName,scalePath):
    log = logging.getLogger('aloha')
    #print scaleName
    #print scalePath
    scale_df=pd.read_csv(scalePath);
    ob=eval(scaleName)(scale_df,'raw');
    oa_miss=ob.miss_DATA();
    #print oa_miss;
    oa_num=ob.pnum();
    oa_dup=ob.isdup();

    oa_range=all(ob.data_range());

    oa_ss={'data missing':[oa_miss],
           'data duplicated':[oa_dup],
           'paticipant number':[oa_num],
           'data in data_range':[oa_range]};
    #oa_st=Series(oa_range,index=ob.lname)
    oa_form=DataFrame(oa_ss);
    #oa_st = pd.DataFrame(np.column_stack(oa_range),columns=ob.lname)
    #oa_form=pd.concat([oa_form, oa_st], axis=1)


    #print oa_form;
    #print oa_st;
    #print oa_num;
    #print oa_dup;
    #print oa_range;
    print tabulate(oa_form,headers=['data duplicated','data in data_range','data missed','paticipant number'],tablefmt='psql');
    if not oa_range:
        print "it seems that we have some data that is out of range, please take a look"
        oa_st=Series(ob.data_range(),index=ob.lname);
        print oa_st;







class Status(Command):
    "Command for exporting data from servers."

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Status, self).get_parser(prog_name)
        parser.add_argument('scaleName', nargs='?', default='.')
        parser.add_argument('scalePath', nargs='?', default='.')

        return parser

    def take_action(self, parsed_args):
        self.log.info('sending greeting')
        self.log.debug('debugging')
        aloha(parsed_args.scaleName,parsed_args.scalePath);

class Error(Command):
    "Always raises an error"

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.info('causing error')
        raise RuntimeError('this is the expected exception')
