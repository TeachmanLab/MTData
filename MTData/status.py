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
import pandas as pd;


SERVER_CONFIG = 'config/server.config';
#logging.config.dictConfig(yaml.load(open('config/recovery_log.config', 'r')))

def aloha(scaleName,scalePath):
    print "checking the status of "+scaleName;
    # checking data status and gernerate report
    log = logging.getLogger('aloha')


    scale_df=pd.read_csv(scalePath);
    try:
        ob=eval(scaleName)(scale_df,True);
    except:
        return "not aloha";
        print "scaleName "+scaleName+" is not correct, please check"
    else:


        oa_miss=ob.miss_DATA().sum();

        oa_num=ob.pnum();
        oa_dup=ob.isdup();
    #oa_nd=ob.drop_dup();
    #oa_nd_num=oa_nd.size;
        oa_range=all(ob.data_range());
        oa_ss={'data missed':[oa_miss],
               'data duplicated':[oa_dup],
               'paticipant number':[oa_num],
               'data in data_range':[oa_range],
               'number of valid entries':[len(ob.drop_dup().axes[0])],
               'total entries numbers':[len(ob.dataset.axes[0])]};
           #columns=['data duplicated','data in data_range','data missed','number of valid entries','paticipant number']};
    #oa_st=Series(oa_range,index=ob.lname)
    #print oa_ss
        oa_form=DataFrame(oa_ss);
    #oa_st = pd.DataFrame(np.column_stack(oa_range),columns=ob.lname)
    #oa_form=pd.concat([oa_form, oa_st], axis=1)

    #print oa_form;
    #print oa_st;
    #print oa_num;
    #print oa_dup;
    #print oa_range;
    # print the result
        print scaleName+" data status";
        print tabulate(oa_form,headers=['data duplicated','data in data_range','data missed','number of valid entries','paticipant number','total entries numbers'],tablefmt='psql',showindex="never");
    # if there is any data out of range print all variables's data range
        if not oa_range:
        #print "....................................................................."
            print "we have some data that is out of range, please take a look"

            oa_st=Series(ob.data_range(),name="out_of_range");
            oa_names=Series(ob.lname,name="variable_names")
        #oa_st = pd.DataFrame(np.column_stack(oa_range),columns=ob.lname)
        #or_df=Series.to_frame(oa_st)
        #or_df.columns
            range_df=pd.concat([oa_names,oa_st], axis=1)
            range_df=range_df[range_df.out_of_range==False]
            print tabulate(range_df,headers=['variable out of range','in the range'],tablefmt='psql',showindex="never");
        # if there is any data out of range print all variables's data range
        #print range_df;
        #print "....................................................................."

        if oa_miss!=0:
        # if there is any data missing print all variables that have missing data
            print "we have some data missing, please take a look"
            miss_df=Series.to_frame(ob.miss_DATA()).reset_index()
            miss_df.columns = ['variable_name', 'missing_number']
            miss_df=miss_df[miss_df.missing_number!=0]



            print tabulate(miss_df,headers=['variable missing','number of missing data'],tablefmt='psql',showindex="never");
        print "checking "+scaleName+"finished"
        print "\n";
        print "\n";
        print "\n";
        return oa_form;



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
            #print config
            return config
    else:
        log.info("severname is wrong")
        return None;

def read_scalename(SERVER_CONFIG,scaleName,scalePath):
    # read server name and scalename and filepath
    if scaleName == "all":
        #if all, then the scalepath is the server name, read path from server.
        config=read_servername(SERVER_CONFIG,scaleName,scalePath);
        filename=(config["PATH"]+'testing_data/benchmark.json');
        #read scalenames from benchmark.json
        with open (filename) as f:
            data=f.read();
        dic=json.loads(data);
        print("read BechMark ok!")
        print dic.keys();
        list_df=[];
        list_scales=[];
        sname_keys=[];
        for sname in dic.keys():
            #print sname;
            #print type(dic.keys());
            #read the newest file of ev;ery scale
            list_scales.append(sname);

            fileList = sorted(glob.glob(config["PATH"]+'testing_data/test_all/'+sname+'*.csv'))

            try:
                newest = max(glob.iglob(config["PATH"]+'testing_data/test_all/'+sname+'*.csv'), key=os.path.getctime)
            except:
                print sname+" files do not exit"
            else:
                df=aloha(sname,newest)
                #print type(df);
                #print df;
                if isinstance(df, basestring):
                    print sname+"is not a valid scaleform"
                else:

                    sname_keys.append(sname);

                    list_df.append(df);

                    all_df=pd.concat(list_df,keys=sname_keys);

                    all_df = all_df.reset_index(level=1,drop=True)


        print tabulate(all_df,headers=['data duplicated','data in data_range','data missed','valid entries','paticipant number','total entries'],tablefmt='psql');

    else:
        aloha(scaleName,scalePath)



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
        read_scalename(SERVER_CONFIG,parsed_args.scaleName,parsed_args.scalePath);

class Error(Command):
    "Always raises an error"

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.info('causing error')
        raise RuntimeError('this is the expected exception')
