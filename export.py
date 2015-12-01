# Install the package is needed:
# DF: (You can't really do that from here, I don't think, but you could abort the app
#     with a thoughtful message ... like "please install 'requests' with pip install requests' and
#     try running again.")
# ------------------------------------------#
# Import the Requests

import requests # To make REST requests of the client.
import time
import os.path
import sys
import rsa # To decrypt values.
import smtplib # to send out notification emails


# ------------------------------------------#
# Set up the server link:
# Use this link for testing phrase 
SERVER='http://localhost:9000/api/export'
USER='daniel.h.funk@gmail.com'
PASS='ereiamjh'
PRIVATE_FILE='private_key.pem'

# Use this link for actual phrase
# SERVER = 'http://localhost:9000/admin/export'

# Get the date
DATE = time.strftime("_%b_%d_%Y")
TIME = time.strftime("%b-%d-%Y %H:%M:%S")


# Set up the SMTP for email notification:
# Use this configuration for testing phrase
SENDER = 'projectimplicitmentalhealth1@gmail.com'
RECEIVER = ['dihengz@gmail.com']
EMAIL = smtplib.SMTP(host='smtp.gmail.com', port='587')

# Use this configuration for actual phrase
# SENDER = 'Server@mindtrails.org'
# RECEIVER = ['mindtrails@virginia.com']
# emails = smtplib.SMTP('##')

# Notification email temple:
TEMPLE = """From: From Faithful Android <%s>
To: To MindTrails Support Team<%s>
X-Priority: 2
Subject: Something goes wrong on MindTrails

Hello,

Sorry to tell you that it seems something is wrong on the MindTrails data collecting server, and below is the error
message:

%s : %s

Hope that you are not sleeping now. Please check it up immediately!

Your faithfully,
Mindtrails Android
"""


# ------------------------------------------#
# Log the running message
def log(m):
    print "I will write this part later"





# Log the error message
def error_log(e):
    if not os.path.exists('logs/Error_log'+DATE+'.txt'):
        output = open('logs/Error_log'+DATE+'.txt', 'w')
        output.write("This is the error information for " + DATE + ", created at " + TIME + ":\n\n")
    output = open('logs/Error_log'+DATE+'.txt', 'a')
    output.write(TIME + " : " + str(e) + "\n")
    output.close()


# Send admin the error message
def notify_admin(e):
    print("YO ADMIN! This should be an email, the problem is:" + str(e))
    message = TEMPLE % (SENDER, RECEIVER, TIME, str(e))
    try:
        EMAIL.ehlo()
        EMAIL.starttls()
        EMAIL.login('projectimplicitmentalhealth1@gmail.com', 'b3BFbaOLuDTe')
        EMAIL.sendmail(SENDER, RECEIVER, message)
        EMAIL.quit()
        message_success = """\n*******************************\nSuccessfully sent email\n""" + message + """***********
        ********************\n"""
        log(message_success)
        print "Successfully sent email"
    except (smtplib.SMTPException, smtplib.SMTPAuthenticationError, smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected, smtplib.SMTPDataError, smtplib.SMTPSenderRefused, smtplib.SMTPResponseException, smtplib.SMTPHeloError) as e:
        error_log(e)
        message_error = """\n*******************************\nError: unable to send email\n""" + message + """*********
        **********************\n"""
        error_log(message_error)
        print "Error: unable to send email"


# Report Important Error, log it down and send an email to admin
def error_notify(e):
    error_log(e)
    notify_admin(e)

# ------------------------------------------#
# Decrypting
with open(PRIVATE_FILE) as privatefile:
    keydata = privatefile.read()
priv_key = rsa.PrivateKey.load_pkcs1(keydata)
def decrypt(crypto):
    if crypto is None: return ""
    message = rsa.decrypt(crypto.decode('base64'), priv_key)
    return message.decode('utf8')


# ------------------------------------------#
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
        error_notify(e)
        raise e  # DF: Callers should handle the exception and continue processing other questionnaires if possible.  



# SafeWrite function, use this to read and save questionnaire data
def safeWrite(data):
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
                for heads in ks[:-1]:
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
#               if scale['deleteable']:
#                    requests.delete(SERVER+'/'+scale['name']+'/'+str(item['id']))
            output.close()


# ------------------------------------------#
# Read the data
oneShot = safeRequest(SERVER)  # DF: Use the method above instead of the direct call.

print(oneShot)

safeWrite(oneShot)

