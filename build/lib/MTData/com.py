# This is the function for combining all the data files for one(or All) scales.
# It takes two argument, name of scales and destination.
# If name = all, combine all the scales in the destination folders.
# The function will return as Scale Object. If name = all, it will return a list(or dict) of objects.
import os
import pandas as pd
import json
import datetime
def combine(scaleList,path):
    if not os.path.exists(path+'/master/'):
        os.makedirs(path+'/master/')
    if scaleList == 'All':
        benchMarkFile = open(path +'/benchMark.json').read()
        scaleList = json.loads(benchMarkFile).keys()
        for scale in scaleList:
            combine(scale,path)
        return("All are done!")
    else:
        fileList = [filename for filename in os.listdir(path) if filename.startswith(scaleList)]
        dataset = pd.DataFrame({'A' : []})
        for files in fileList:
            if dataset.empty:
                dataset = pd.read_csv(path+'/'+files)
                print dataset
            else:
                temp_dataset = pd.read_csv(path+'/'+files)
                dataset = pd.concat([dataset,temp_dataset],ignore_index=True)
                print dataset
        dataset.to_csv(path+'/master/'+scaleList+'_'+datetime.datetime.now().strftime("%Y-%m-%d")+'_master.csv')
        return dataset
