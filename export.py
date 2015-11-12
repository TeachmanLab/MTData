# Install the package is needed:
# DF: (You can't really do that from here, I don't think, but you could abort the app
#     with a thoughtful message ... like "please install 'requests' with pip install requests' and
#     try running again.")

# Import the Requests

import requests # To make REST requests of the client.
import time
import os.path
import sys
import rsa # To decrypt values.

# Set up the server link:
# Use this link for testing phrase 
SERVER='http://localhost:9000/api/export'
USER='daniel.h.funk@gmail.com'
PASS='ereiamjh'
PRIVATE_FILE='private_key.pem'

# Use this link for actual phrasse
# SERVER = 'http://localhost:9000/admin/export'

# Get the date
DATE = time.strftime("_%d_%m_%Y")



def notify_admin(e):
    print("YO ADMIN! This should be an email, the problem is:" + str(e))



with open(PRIVATE_FILE) as privatefile:
    keydata = privatefile.read()
priv_key = rsa.PrivateKey.load_pkcs1(keydata)
def decrypt(crypto):
    if crypto is None: return ""
    try:
        message = rsa.decrypt(crypto.decode('base64'), priv_key)
        return message.decode('utf8')
    except Exception as ex:
        template = "Failed to decrypt a value, might not have been encrypted in the first place.  Storing it raw.  When decyrpting received an error of type {0}. Arguments:{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print message
        return crypto
        
# DF: Should likely write our own method that will make the request and return
# a json response, since things can go wrong here in lots of ways and we want
# to try and catch all of them. In this way we can handle exceptions, emailing
# us in the event of an error. THIS CODE IS NOT COMPLETE. I'm just roughly
# trying to show what it should do.
def safeRequest(url):
    try:
        # DF: Make request, and check the status code of the response.
        response = requests.get(url, auth=(USER,PASS))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:  # DF: We may loose some detail here, better to check all exceptions.
        print e
        notify_admin(e)
        raise e  # DF: Callers should handle the exception and continue processing other questionnaires if possible.  
        
# Read the data
data = safeRequest(SERVER)  # DF: Use the method above instead of the direct call.

# One by one, read out the data form names(scale names) in d, and then:
for scale in data:
    #DF: Should write something to a log file in here somewhere recording # of records exported for each
    quest = safeRequest(SERVER+'/'+scale['name'])
    if scale['size'] != 0:
        ks = list(quest[0].keys())
        ks.sort()

#A\ Check if there is a file named [form_name]_[date].csv in the Active Data Pool, if not, create one 

        if not os.path.exists('active_data/'+scale['name']+DATE+'.csv'):
            output = open('active_data/'+scale['name']+DATE+'.csv','w')
            for heads in ks: 
                output.write(heads+'\t')
            output.write(ks[-1]+'\n')
            output.close()
 #B\ Open [form_name]_[date].csv, append the data we have into it, one by one. 
        
        output = open('active_data/'+scale['name']+DATE+'.csv','a')
        for item in quest:
            for key in ks:                
                if(key.endswith("RSA")): value = decrypt(item[key])
                elif item[key] is None: value = ""
                else: value = str(item[key]) # could be an int, make sure it is a string so we can encode it.
                output.write(value.encode('utf-8') + "\t")
            output.write("\n")
            #[And then send back delete commend one by one]            
#            if scale['deleteable']: 
#                requests.delete(SERVER+'/'+scale['name']+'/'+str(item['id']))
        output.close()


