# ------------------------------------------#
# Import the Requests

import requests # To make REST requests of the client.
import time
import os.path
import rsa # To decrypt values.
import csv # To write the data into CSV file safely
import binascii
import logging
import logging.config
import yaml

# ------------------------------------------#

# Set up logging config files
logging.config.dictConfig(yaml.load(open('log.config', 'r')))

# Load the Configuration file
if __name__ == "__main__":
    config = {}
    execfile("export.config", config)


# Decrypting
with open(config["PRIVATE_FILE"]) as privatefile:
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


# Setting up files directories and logging config files
if not os.path.exists(config["PATH"]+"logs/"): # Can't find a better way to do this......
    os.makedirs(config["PATH"]+"logs/")
logging.config.dictConfig(yaml.load(open('log.config', 'r')))


# ------------------------------------------#

def safeKeep(scaleName, response, file):
    log = logging.getLogger('export.safeKeep')
    stamp = time.strftime(config["TIME_FORMAT"])
    try:
        with open(file, 'a') as dataJson:
           dataJson.write(response.text.encode('utf-8'))
        return True
    except:
        log.critical(scaleName + ' data backup failed, immediate attention needed.\n', exc_info = 1)
        return False

# DF: Should likely write our own method that will make the request and return
# a json response, since things can go wrong here in lots of ways and we want
# to try and catch all of them. In this way we can handle exceptions, emailing
# us in the event of an error. THIS CODE IS NOT COMPLETE. I'm just roughly
# trying to show what it should do.
def safeRequest(url):
    log = logging.getLogger('export.safeRequest')
    log.info("Trying to Request data for %s ......", url)
    try:
        response = requests.get(url, auth=(config["USER"],config["PASS"]))
        m = response.raise_for_status()
        log.info("Data request successfully, see below for request detail:\n%s\nIssues: %s", url, str(m)) # Log successful data request
        if response != None:
            try:
                data = response.json()
                log.info("We got something new! Let's have a closer look!")
                return response
            except:
                log.critical("Can't read data in json form. Did not receive a json response, perhaps log-in credentials are incorrect? See below for error information:\n", exc_info = 1)
    except requests.exceptions.Timeout:
        log.critical("Data request timed out for url: " + url + ". See below for error information:\n", exc_info = 1)
    except requests.exceptions.TooManyRedirects:
        log.critical("Too many redirects for url: " + url + ". See below for error information:\n", exc_info = 1)
    except requests.exceptions.RequestException as e:  # DF: We may loose some detail here, better to check all exceptions.
        log.critical("Data request failed, fatal, emailed admin. Error was " + str(e) + " see below for error information:\n", exc_info = 1)


# SafeDelete function, use this to delete data entries and log down system message
def safeDelete(url):
    log = logging.getLogger('export.safeDelete')
    log.info("Trying to Delete data for %s ......", url)
    try:
        # DH: Make request, delete and check the status code of the response.
        delete = requests.delete(url, auth=(config["USER"],config["PASS"]))
        m = delete.raise_for_status()
        log.info("Data delete successfully, see below for request detail:\n%s\nIssues: %s", url, str(m)) # Log successful data delete
        return True
    except requests.exceptions.RequestException as e:  # DF: We may loose some detail here, better to check all exceptions.
        log.critical("Data delete failed, fatal, emailed admin. see below for error information:\n", exc_info = 1)
        return False


# SafeWrite function, use this to write questionnaire data into csv files
def safeWrite(response, date_file, raw_file, ks, scaleName, deleteable):
#B\ Open [form_name]_[date].csv, append the data we have into it, one by one.
    log = logging.getLogger('export.safeWrite')
    log.info("Writing new entries from %s to %s: writing in progress......", scaleName, date_file)
    backup = safeKeep(scaleName, response, raw_file)
    quest = response.json()
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
                    except UnicodeEncodeError:
                        log.error("Data encode failed, data lost. Questionnaire: %s, Entry ID: %s, Field: %s", scaleName, entry['id'], key, exc_info = 1) # Should log error, entry ID and data field
                else: entry[key] = ""
            try:
                dataWriter.writerow(entry)
                t += 1
                log.debug("%s entries wrote successfully.", str(t))
                if deleteable and backup and config["DELETE_MODE"]:                              # If the scale is deleteable, delete the entry after it is successfully recorded.
                    if safeDelete(config["SERVER"] + '/' + scaleName + '/' + str(entry['id'])): d += 1 # If deleting success, d increase.
                else: log.info('Questionnaire - %s, ID - %s, data cleaning on hold. Detail: Deleteable: %s, Backup: %s, Delete Mode: %s', scaleName, str(entry['id']), str(deleteable), str(backup), str(config["DELETE_MODE"]))
            except csv.Error:
                error += 1
                log.critical("Failed in writing entry, Questionnaire: %s, Entry ID: %s", scaleName, entry['id'], exc_info = 1)
        log.info("Questionnaire %s update finished - %s new entries recoded successfully.", scaleName, str(t))
        log.info("Questionnaire %s data cleaning finished - %s new entries successfully deleted on MindTrails.", scaleName, str(d))
        if error > 0:
            log.critical("Questionnaire %s update error - %s new entries failed to recode.", scaleName, str(error))



# Create data files with date as name:
def createFile(file, ks):
    log = logging.getLogger('export.createFile')
    if not os.path.exists(file): # Create new file if file doesn't exist
        with open(file, 'w') as datacsv:
            headerwriter = csv.DictWriter(datacsv, dialect='excel', fieldnames= ks)
            try:
                headerwriter.writeheader()
                log.info("New data file created: %s", file)
            except csv.Error:
                log.critcal("Failed to create new data files, fatal, emailed admin.", exc_info=1)


# Main function, use this to read and save questionnaire data
def safeExport(data):
# One by one, read out the data form names(scale names) in d, and then:
    log = logging.getLogger('export.safeExport')
    s = 0
    log.info("Database update in progress......")
    for scale in data:
        response = safeRequest(config["SERVER"]+'/'+scale['name'])
        if response!= None:
            quest = response.json()
            if quest != None:
                if scale['size'] != 0:
                    ks = list(quest[0].keys())
                    ks.sort()
                    log.info("Questionnaire %s updated - %s new entries received.", str(scale['name']), str(scale['size']))
                    #A\ Check if there is a file named [form_name]_[date].csv in the Active Data Pool, if not, create one
                    date_file = config["PATH"] + 'active_data/'+ scale['name'] + '_' + time.strftime(config["DATE_FORMAT"]) +'.csv'
                    raw_file = config["PATH"] + 'raw_data/' + scale['name'] + '_' + time.strftime(config["DATE_FORMAT"] + '_' + time.strftime(config["TIME_FORMAT"]) +'.json')
                    createFile(date_file, ks)  # Create a new data file with Date in name for decrypted data if not already exists
                    safeWrite(response, date_file, raw_file, ks, str(scale['name']), scale['deleteable']) # Safely write the whoe questionnaire into the data file
                    s += 1
                else: log.info("No new entries found in %s", str(scale['name']))
            else:
                log.warning("""This is weired... It seems that there is nothing out there or I am blocked from MindTrails. You might already get an email from me
                reporting some network issues. Be alerted, stay tuned.""")
    log.info("Database update finished: %s questionnaires' data updated.", str(s))

def pathCheck():
    log = logging.getLogger('export.pathCheck')
    try:
        if not os.path.exists(config["PATH"]+"raw_data/"):
            os.makedirs(config["PATH"]+"raw_data/")
            log.info("Successfully created raw_data folder.")
        if not os.path.exists(config["PATH"]+"active_data/"):
            os.makedirs(config["PATH"]+"active_data/")
            log.info("Successfully created active_data folder.")
    except:
        log.critical("Failed to create data or log files, fatal, emailed admin.", exc_info=1)

# ------------------------------------------#
# This is the main module
def export():

    log = logging.getLogger('export')
    log.info("""Hi PACT Lab, this is faithful android Martin from Laura\'s server. Everything is alright here, and seems to be
     a good time for a hunt. I am going out for a regular check and will come back soon. Don't miss me PACT Lab, it wouldn't
     take too long.""")
    pathCheck() #Check storage path
    log.info(" (Martin is out for hunting data......) ")
    oneShot = safeRequest(config["SERVER"])
    if oneShot != None:
        log.info("""Alright I am back! Pretty fruitful. Seem like it is going to be comfortable for a little while. Alright,
     I am heading to the server for a little rest, will talk to you guys in PACT Lab in a little while. -- Martin""")
        if (oneShot.json() != None): safeExport(oneShot.json())
    else:
        log.warning("""This is weired... It seems that there is nothing out there or I am blocked from MindTrails. You might already get an email from me
     reporting some network issues. Be alerted, stay tuned.""")
    log.info("I am tired and I am going back to Laura's server for a rest. See you later!")



# Works here:
export()
