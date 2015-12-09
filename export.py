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
DATE_FORMAT = "%b_%d_%Y"

# Decrypting
with open(PRIVATE_FILE) as privatefile:
    keydata = privatefile.read()
priv_key = rsa.PrivateKey.load_pkcs1(keydata)
def decrypt(crypto, id, scaleName, field):
    log = logging.getLogger('export.decrypt')
    if crypto is None: return ""
    try:
        value = crypto.decode('base64')
        log.info('Decode successfully.')
        try:
            message = rsa.decrypt(value, priv_key)
            log.info('Decrypt successfully.')
            return message.decode('utf8')
        except (rsa.pkcs1.CryptoError, rsa.pkcs1.DecryptionError):
            log.error('Decrypt failed, original value recorded. Questionnaire = %s, Entry ID: %s, Field: %s See information:', scaleName, id, field, exc_info = 1)
            return crypto
    except (UnicodeDecodeError, binascii.Error):
        log.error('Decode failed, item skipped. Questionnaire = %s, Entry ID: %s, Field: %s See information:', scaleName, id, field, exc_info = 1)

# ------------------------------------------#
# DF: Should likely write our own method that will make the request and return
# a json response, since things can go wrong here in lots of ways and we want
# to try and catch all of them. In this way we can handle exceptions, emailing
# us in the event of an error. THIS CODE IS NOT COMPLETE. I'm just roughly
# trying to show what it should do.
def safeRequest(url):
    log = logging.getLogger('export.safeRequest')
    log.info("Trying to Request data for %s ......", url)
    try:
        # DF: Make request, and check the status code of the response.
        response = requests.get(url, auth=(USER,PASS))
        m = response.raise_for_status()
        log.info("Data request successfully, see below for request detail:\n%s\nIssues: %s", url, str(m)) # Log successful data request
        return response.json()
    except requests.exceptions.RequestException:  # DF: We may loose some detail here, better to check all exceptions.
        log.critical("Data request failed, fatal, emailed admin. see below for error information:\n", exc_info = 1)

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
def safeWrite(quest, date_file, ks, scaleName):
#B\ Open [form_name]_[date].csv, append the data we have into it, one by one.
    log = logging.getLogger('export.safeWrite')
    log.info("Writing new entries from %s to %s: writing in progress......", scaleName, date_file)
    with open(date_file, 'a') as datacsv:
        dataWriter = csv.DictWriter(datacsv, dialect='excel', fieldnames= ks)
        t = 0
        error = 0
        d = 0
        for entry in quest:
            for key in ks:
                if(key.endswith("RSA")): value = decrypt(entry[key], entry['id'], scaleName, key)
                elif entry[key] is None: value = ""
                else: value = str(entry[key]) # could be an int, make sure it is a string so we can encode it.
                if (value != None):
                    try:
                        entry[key] = value.encode('utf-8')
                        log.debug("Data successfully encoded.")
                    except UnicodeEncodeError as e:
                        log.error("Data encode failed, data lost. Questionnaire: %s, Entry ID: %s, Field: %s", scaleName, entry['id'], key, exc_info = 1) # Should log error, entry ID and data field
                else: entry[key] = ""
            try:
                dataWriter.writerow(entry)
                t += 1
                log.debug("%s entries wrote successfully.", str(t))
            except csv.Error:
                error += 1
                log.error("Failed in writing entry, Questionnaire: %s, Entry ID: %s", scaleName, entry['id'], exc_info = 1)
        log.info("Questionnaire %s update finished - %s new entries recoded successfully.", scaleName, str(t))
        if error > 0:
            log.error("Questionnaire %s update error - %s new entries failed to recode.", scaleName, str(error))
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
                        log.info("New data file created: %s", date_file)
                    except csv.Error:
                        log.critcal("Failed to create new data files, fatal, emailed admin.", exc_info=1)

# Main function, use this to read and save questionnaire data
def safeExport(data):
# One by one, read out the data form names(scale names) in d, and then:
    log = logging.getLogger('export.safeExport')
    s = 0
    log.info("Database update in progress......")
    for scale in data:
        #DF: Should write something to a log file in here somewhere recording # of records exported for each
        quest = safeRequest(SERVER+'/'+scale['name'])
        if quest != None:
            if scale['size'] != 0:
                ks = list(quest[0].keys())
                ks.sort()
                log.info("Questionnaire %s updated - %s new entries received.", str(scale['name']), str(scale['size']))
#A\ Check if there is a file named [form_name]_[date].csv in the Active Data Pool, if not, create one 
                date_file = 'active_data/'+ scale['name'] + '_' + time.strftime(DATE_FORMAT) +'.csv'
                createFile(date_file, ks)  # Create a new data file with Date in name if not already exists
                safeWrite(quest, date_file, ks, str(scale['name'])) # Safely write the whoe questionnaire into the data file
                s += 1
            else: log.info("No new entries found in %s", str(scale['name']))
        else:
            log.warning("""This is weired... It seems that there is nothing out there or I am blocked from MindTrails. You might already get an email from me
     reporting some network issues. Be alerted, stay tuned.""")
    log.info("Database update finished: %s questionnaires' data updated.", str(s))

# ------------------------------------------#
# This is the main module
def export():

    log = logging.getLogger('export')
    log.info("""Hi PACT Lab, this is faithful android Martin from Laura\'s server. Everything is alright here, and seems to be
     a good time for a hunt. I am going out for a regular check and will come back soon. Don't miss me PACT Lab, it wouldn't
     take too long.""")
    log.info(" (Martin is out for hunting data......) ")
    oneShot = safeRequest(SERVER)  # DF: Use the method above instead of the direct call.
    if oneShot != None:
        log.info("""Alright I am back! Pretty fruitful. Seem like it is going to be comfortable for a little while. Alright,
     I am heading to the server for a little rest, will talk to you guys in PACT Lab in a little while. -- Martin""")
        safeExport(oneShot)
    else:
        log.warning("""This is weired... It seems that there is nothing out there or I am blocked from MindTrails. You might already get an email from me
     reporting some network issues. Be alerted, stay tuned.""")


export()
