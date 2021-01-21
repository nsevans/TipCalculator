import time
import math
import os

from flask import abort

import schedule
import threading

import common.event_logger as logger
import common.settings as settings

global lastBeatTime
lastBeatTime = time.time()

global job_started
job_started = False

def runJob():
    """
    Job that runs every x amount of seconds to keep the server alive.
    """
    global lastBeatTime
    global job_started
    
    curTime = time.time()
    
    if job_started:
        # Check if specified amount of time has passed since last keep alive token was sent
        # If token missed deadline, close down server
        if(math.floor(curTime) - math.floor(lastBeatTime) > settings.app_settings['KEEP_ALIVE_TIMEOUT']):
            logger.logEvent('Keep Alive token missed deadline after '+str(settings.app_settings["KEEP_ALIVE_TIMEOUT"])+'s, shutting down server...\n')
            settings.write_updated_settings_to_file()
            time.sleep(1)
            os._exit(1)

    elif math.floor(curTime) - math.floor(lastBeatTime) > settings.app_settings["MAX_TIMEOUT"]:
        logger.logEvent('Initial Keep Alive token never arrived after '+str(settings.app_settings["MAX_TIMEOUT"])+'s, shutting down server...\n')
        settings.write_updated_settings_to_file()
        time.sleep(1)
        os._exit(1)

def scheduleThread():
    """
    Called to run the keepAliveJob function every x seconds.
    """
    while True:
        schedule.run_pending()
        time.sleep(settings.app_settings['KEEP_ALIVE_TIMEOUT'])

def startJob():
    """
    Setup the thread and the job to let the server stay alive as long as client is active.
    """
    try:
        schedule.every(settings.app_settings['KEEP_ALIVE_TIMEOUT']).seconds.do(runJob)
        thread = threading.Thread(target=scheduleThread, daemon=True)
        thread.start()
    except Exception as e:
        logger.logTraceback('---'+str(e)+'---', e)
        abort(500, description=e)

def resetWaitTime():
    global lastBeatTime
    lastBeatTime = time.time()