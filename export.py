# Install the package is needed:


# Import the Requests

import requests
import time
import os.path
import sys

# Set up the server link:
# Use this link for testing prahse 
SERVER = 'http://localhost:9000/public/export'

# Use this link for actual prahse
# SERVER = 'http://localhost:9000/public/export'

# Get the date
DATE = time.strftime("_%d_%m_%Y")

# Read the data
r = requests.get(SERVER)

data = r.json()

# One by one, read out the data form names(scale names) in d, and then:

for scale in data:
    quest = requests.get(SERVER+'/'+scale['name'])
    quest = quest.json()
    if scale['size'] != 0:
        ks = list(quest[0].keys())
        ks.sort()

#A\ Check if there is a file named [form_name]_[date].csv in the Active Data Pool, if not, create one 

        if not os.path.exists('active_data/'+scale['name']+DATE+'.csv'):
            output = open('active_data/'+scale['name']+DATE+'.csv','w')
            for heads in ks[:-1]: 
                output.write(heads+'\t')
            output.write(ks[-1]+'\n')
            output.close()

#B\ Open [form_name]_[date].csv, append the data we have into it, one by one. 
        
        output = open('active_data/'+scale['name']+DATE+'.csv','a')
        for item in quest:
            for key in ks[:-1]:
                output.write((item[key].encode('utf-8') if isinstance(item[key],unicode) else str(item[key]))+'\t')
            output.write((item[ks[-1]].encode('utf-8') if isinstance(item[ks[-1]],unicode) else str(item[key]))+'\n')
            #[And then send back delete commend one by one]            
#            if scale['deleteable']: 
#                requests.delete(SERVER+'/'+scale['name']+'/'+str(item['id']))
        output.close()


