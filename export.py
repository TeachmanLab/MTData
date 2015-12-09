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
import csv # To write the data into CSV file safely
import binascii
import logging
import logging.config
import yaml


# ------------------------------------------#

# Set up logging config files
logging.config.dictConfig(yaml.load(open('log.config', 'r')))


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
def setLog():
    log = logging.getLogger('debug')
    log.info('Trying!')
    log1 = logging.getLogger('daily')
    log1.info('Trying! This is an error!')

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
    log = logging.getLogger('export.decrypt')
    if crypto is None: return ""
    try:
        value = crypto.decode('base64')
        log.info('Decode successfully.')
        try:
            message = rsa.decrypt(value, priv_key)
            log.info('Decrypt successfully.')
            return message.decode('utf8')
        except (rsa.pkcs1.CryptoError, rsa.pkcs1.DecryptionError) as e:
            error_notify(e)
            log.error('Decrypt failed, original value recorded. See information: %s', str(e), exc_info = 1)
            print "Decrypt failed:" + str(e)
            return crypto
    except (UnicodeDecodeError, binascii.Error) as e:
        log.error('Decode failed, item skipped. See information: %s', str(e), exc_info = 1)
        # log(e)
        print "Decode Failed:" + str(e)






# ------------------------------------------#
# DF: Should likely write our own method that will make the request and return
# a json response, since things can go wrong here in lots of ways and we want
# to try and catch all of them. In this way we can handle exceptions, emailing
# us in the event of an error. THIS CODE IS NOT COMPLETE. I'm just roughly
# trying to show what it should do.
def safeRequest(url):
    log = logging.getLogger('export.safeRequest')
    try:
        # DF: Make request, and check the status code of the response.
        response = requests.get(url, auth=(USER,PASS))
        m = response.raise_for_status()
        message = "Data request successfully, see below for request detail:\n"
        log.info(message + url + "\n" + "Error: " + str(m)) # DH: Log success data request
        print message + str(m)
        return response.json()
    except requests.exceptions.RequestException as e:  # DF: We may loose some detail here, better to check all exceptions.
        message = "Data request failed, see below for error information:\n"
        log.error(message + str(e), exc_info = 1)
        log.critical(str(e), exc_info = 1)

     # DF: Callers should handle the exception and continue processing other questionnaires if possible.



# SafeDelete function, use this to delete data entries and log down system message
def safeDelete(url):
    log = logging.getLogger('export.safeDelete')
    try:
        # DH: Make request, and check the status code of the response.
        delete = requests.delete(url, auth=(USER, PASS))
        m = delete.raise_for_status()
        message = "Data delete successfully, see below for deleting detail:\n"
        log.info(message + url + "\n" + "Error: " + str(m)) # DH: Log successful data delete request
        print message + str(m)
        return True
    except requests.exceptions.RequestException as e:  # DF: We may loose some detail here, better to check all exceptions.
        message = "Data delete failed, see below for error information:\n"
        log.error(message + str(e), exc_info = 1)
        log.critical(str(e), exc_info = 1)
        print e # DF: Callers should handle the exception and continue processing other questionnaires if possible.



# SafeWrite function, use this to write questionnaire data into csv files
def safeWrite(quest, date_file, ks, message):
#B\ Open [form_name]_[date].csv, append the data we have into it, one by one.
    log = logging.getLogger('export.safeWrite')
    with open(date_file, 'a') as datacsv:
        dataWriter = csv.DictWriter(datacsv, dialect='excel', fieldnames= ks)
        t = 0
        error = 0
        d = 0
        for entry in quest:
            for key in ks:
                if(key.endswith("RSA")): value = decrypt(entry[key])
                elif entry[key] is None: value = ""
                else: value = str(entry[key]) # could be an int, make sure it is a string so we can encode it.
                if (value != None):
                    try:
                        entry[key] = value.encode('utf-8')
                    except UnicodeEncodeError as e:
                        log.error(str(e), exc_info = 1) # Should log error, entry ID and data field
                else: entry[key] = ""
            try:
                dataWriter.writerow(entry)
                t += 1
            except csv.Error as e:
                error += 1
                log.error("Should put updated logging information here", exc_info = 1)
            log.info(message + str(t) + " new entries recorded.")
            log.info("How many entry failed to record.")

#           if scale['deleteable']:
#             safeDelete(SERVER+'/'+scale['name']+'/'+str(entry['id'])) #[And then send back delete commend one by one]
#             d += 1
#           log.info(message + str(d) + " entries deleted.")


# Create data files with date as name:
def createFile(date_file, ks):
    log = logging.getLogger('export.createFile')
    if not os.path.exists(date_file): # Create new file if file doesn't exist
                with open(date_file, 'w') as datacsv:
                    headerwriter = csv.DictWriter(datacsv, dialect='excel', fieldnames= ks)
                    try:
                        headerwriter.writeheader()
                        log.info("New data file created: " + date_file)
                    except csv.Error as e:
                        log.error("Failed to create new data files, fatal, email admin", exc_info=1)

# Main function, use this to read and save questionnaire data
def safeExport(data):
# One by one, read out the data form names(scale names) in d, and then:
    log = logging.getLogger('export.safeExport')
    for scale in data:
        #DF: Should write something to a log file in here somewhere recording # of records exported for each
        quest = safeRequest(SERVER+'/'+scale['name'])
        if scale['size'] != 0:
            ks = list(quest[0].keys())
            ks.sort()
            message = "Questionnaire " + str(scale['name']) + " updated - "
            log.info(message + str(scale['size']) + " new entries exported.")
#A\ Check if there is a file named [form_name]_[date].csv in the Active Data Pool, if not, create one 
            date_file = 'active_data/'+scale['name'] + '_' + DATE+'.csv'
            createFile(date_file, ks)  # Create a new data file with Date in name if not already exists
            safeWrite(quest, date_file, ks, message)  # Safely write the whoe questionnaire into the data file



# ------------------------------------------#
# Read the data
oneShot = safeRequest(SERVER)  # DF: Use the method above instead of the direct call.

print(oneShot)

safeExport(oneShot)

setLog()
