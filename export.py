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
DATE = time.strftime("%b_%d_%Y")
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
    log_file = 'logs/Log_'+DATE+'.txt'
    if not os.path.exists(log_file):
        output = open(log_file, 'w')
        output.write("This is the server log for " + DATE + ", created at " + TIME + ":\n\n")
    output = open(log_file, 'a')
    output.write(TIME + " : " + str(m) + "\n")
    output.close()
    print "New information in log file"



# Log the error message
def error_log(e):
    log_file = 'logs/Error_log_'+DATE+'.txt'
    if not os.path.exists(log_file):
        output = open(log_file, 'w')
        output.write("This is the error information for " + DATE + ", created at " + TIME + ":\n\n")
    output = open(log_file, 'a')
    output.write(TIME + " : " + str(e) + "\n")
    output.close()
    print "New information in error log file"


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
        message_success = """\n*******************************\nSuccessfully sent email\n""" + message + """*******************************"""
        log(message_success)
        print "Successfully sent email"
    except (smtplib.SMTPException, smtplib.SMTPAuthenticationError, smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected, smtplib.SMTPDataError, smtplib.SMTPSenderRefused, smtplib.SMTPResponseException, smtplib.SMTPHeloError) as e:
        error_log(e)
        message_error = """\n*******************************\nError: unable to send email\n""" + message + """*******************************"""
        error_log(message_error)
        log("Error: unable to send email, see error log file for detail.")
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
    try:
        message = rsa.decrypt(crypto.decode('base64'), priv_key)
        return message.decode('utf8')
    except (rsa.pkcs1.CryptoError, rsa.pkcs1.DecryptionError) as e:
        error_notify(e)
        print "Decrypt failed:" + str(e)
        raise e



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
        m = response.raise_for_status()
        message = "Data request successfully, see below for request detail:\n"
        log(message + url + "\n" + "Error: " + str(m)) # DH: Log success data request
        print message + str(m)
        return response.json()
    except requests.exceptions.RequestException as e:  # DF: We may loose some detail here, better to check all exceptions.
        message = "Data request failed, see below for error information:\n"
        log(message + str(e))
        error_notify(e)

        raise e  # DF: Callers should handle the exception and continue processing other questionnaires if possible.



# SafeDelete function, use this to delete data entries and log down system message
def safeDelete(url):
    try:
        # DH: Make request, and check the status code of the response.
        delete = requests.delete(url, auth=(USER, PASS))
        m = delete.raise_for_status()
        message = "Data delete successfully, see below for deleting detail:\n"
#        log(message + url + "\n" + "Error: " + str(m)) # DH: Log success data request
        print message + str(m)
        return True
    except requests.exceptions.RequestException as e:  # DF: We may loose some detail here, better to check all exceptions.
        message = "Data delete failed, see below for error information:\n"
        log(message + str(e))
        error_notify(e)
        raise e # DF: Callers should handle the exception and continue processing other questionnaires if possible.


# SafeWrite function, use this to read and save questionnaire data
def safeWrite(data):
# One by one, read out the data form names(scale names) in d, and then:
    for scale in data:
        #DF: Should write something to a log file in here somewhere recording # of records exported for each
        quest = safeRequest(SERVER+'/'+scale['name'])
        if scale['size'] != 0:
            ks = list(quest[0].keys())
            ks.sort()
            message = "Questionnaire " + str(scale['name']) + " updated - "
            log(message + str(scale['size']) + " new entries exported.")

#A\ Check if there is a file named [form_name]_[date].csv in the Active Data Pool, if not, create one 
            date_file = 'active_data/'+scale['name'] + '_' + DATE+'.csv'
            if not os.path.exists(date_file):
                output = open(date_file,'w')
                for heads in ks[:-1]:
                    output.write(heads+'\t')
                output.write(ks[-1]+'\n')
                output.close()
                log("New data file created: " + date_file)
            
#B\ Open [form_name]_[date].csv, append the data we have into it, one by one. 
        
            output = open(date_file,'a')
            t = 0
            d = 0
            for entry in quest:
                for key in ks:
                    if(key.endswith("RSA")): value = decrypt(entry[key])
                    elif entry[key] is None: value = ""
                    else: value = str(entry[key]) # could be an int, make sure it is a string so we can encode it.
                    output.write(value.encode('utf-8') + "\t")
                output.write("\n")
                t += 1
#                if scale['deleteable']:
#                    safeDelete(SERVER+'/'+scale['name']+'/'+str(entry['id'])) #[And then send back delete commend one by one]
#                    d += 1
                log(message + str(t) + " new entries recorded.")
#                log(message + str(d) + " entries deleted.")
            output.close()


# ------------------------------------------#
# Read the data
oneShot = safeRequest(SERVER)  # DF: Use the method above instead of the direct call.

print(oneShot)

safeWrite(oneShot)

