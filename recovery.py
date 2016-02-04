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
import pickle

# ------------------------------------------#
# Load the Configuration file
if __name__ == "__main__":
    config = {}
    execfile("export.config", config)

# Check the path before doing anything
def pathCheck():
    log = logging.getLogger('recovery.pathCheck')
    if not os.path.exists(config["PATH"]+"raw_data/"):
        log.error("No raw_data folder is found, please double check before continuing.")
        print("No raw_data folder is found, please double check before continuing.")
        return False
    if not os.path.exists(config["PATH"]+"recovery_data/"):
        try:
            os.makedirs(config["PATH"]+"recovery_data/")
            log.info("Successfully created recovery_data folder.")
            print("Successfully created recovery_data folder.")
            return True
        except:
            log.critical("Failed to create data folders, fatal, emailed admin.", exc_info=1)
            print("Failed to create data folders, fatal, emailed admin.")
            return False
    else: return True

# Read in files here and recover the data
def safeRecover(scaleName,ALL,startDate,endDate):
    log = logging.getLogger('recovery.safeRecover')
    print("Say hi!")



# Take your order so that we know what scale and how much data you want to recover:
def takeOrder():
    log = logging.getLogger('recovery.takeOrder')
    scaleName = str(raw_input("""Please enter the scale name that you would like
        to recover data for. Reminder: Type in the name exactly as it is on the
        raw data files.\nscaleName:"""))
    print("Thanks!\n")
    startDate = str(raw_input("""Please enter the start date of the data that you
        would like to recover. If you want to recover all the raw data avaliable
        for this scale, please enter "All". Format: Jan_01_1900 or All. \nstartDate:"""))
    if startDate == "All":
        ALL = True
    else:
        ALL = False
    if not ALL:
        endDate = str(raw_input("""Please enter the end date of the data that you
        would like to recover. Format: Jan_01_1900\nendDate:"""))
        log.info("Recovered scale name:%s\nFrom:%s\nTo:%s\n",scaleName,startDate,endDate)
        print("Recovered scale name:%s\nFrom:%s\nTo:%s\n",scaleName,startDate,endDate)
    else:
        startDate = "NA"
        endDate = "NA"
        log.info("Recovered scale name:%s\nRange: ALL",scaleName)
        print("Recovered scale name:%s\nRange: ALL",scaleName)
    safeRecover(scaleName,ALL,startDate,endDate)

# ------------------------------------------#
# This is the main module
def recovery():
    log = logging.getLogger('recovery')
    print("Hello there!")
    if pathCheck():
        log.info("Data Recovery tried at %s, %s",time.strftime(config["DATE_FORMAT"]), time.strftime(config["TIME_FORMAT"]))
        print("Data Recovery tried at %s, %s",time.strftime(config["DATE_FORMAT"]), time.strftime(config["TIME_FORMAT"]))
        takeOrder()
    else:
        log.info("No raw data found or recovery data folder failed to be created. Please check before trying again. Thanks!")
        print("No raw data found or recovery data folder failed to be created. Please check before trying again. Thanks!")


# Works here:
recovery()
