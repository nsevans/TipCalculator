import logging
import logging.handlers
import traceback
import datetime



import common.utils as utils
import common.settings as settings

def init_logger(name, log_file, message_format, level=logging.INFO):
    """
    Setup the logger with the correct log file and message formatting.

    Args:
        name (string): The name of the logger.
        log_file (string): The file the logger will be writing to.
        message_format (string): The format of each log that will be written (Usually contains time, log level and message).
        level (int, optional): The level of importance of a message (INFO, WARNING, DEBUGERROR, CRITICAL). Defaults to logging.INFO.

    Returns:
        logging.Logger: New instance of a logger with all the appropriate setup
    """
    handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=settings.app_settings['MAX_LOG_SIZE_BYTES'], 
                                                    backupCount=settings.app_settings['MAX_LOG_FILE_COUNT'])
    handler.setFormatter(logging.Formatter(message_format))

    newLogger = logging.getLogger(name)
    newLogger.setLevel(level)
    newLogger.addHandler(handler)
    newLogger.propagate = False

    return newLogger


# Initialize each type of logger for the server
eventLogger = init_logger('Event Logger', settings.app_settings["EVENT_LOG"], '<%(asctime)s> %(levelname)s: %(message)s')
errorLogger = init_logger('Error Logger', settings.app_settings["ERROR_LOG"], '<%(asctime)s> %(levelname)s: %(message)s', level=logging.WARNING)
tracebackLogger = init_logger('Traceback Logger', settings.app_settings["TRACEBACK_LOG"], '%(message)s')

def logEvent(message, log_type=logging.INFO, logger=eventLogger):
    """
    Base logging function.

    Args:
        message (string): Description of events.
        log_type (int, optional): The importance/type of log. Defaults to logging.INFO.
        logger (logging.Logger, optional): Instance of a logger. Defaults to eventLogger.
    """

    console_output = ''
    if log_type == logging.INFO:
        logger.info(message)
        console_output = 'INFO '+message

    elif log_type == logging.DEBUG :
        logger.debug(message)
        console_output = 'DEBUG '+message

    elif log_type == logging.WARNING:
        logger.warning(message)
        console_output = 'WARNING '+message

    elif log_type == logging.ERROR:
        logger.error(message)
        console_output = 'ERROR '+message

    elif log_type == logging.CRITICAL:
        logger.critical(message)
        console_output = 'CRITICAL '+message
    
    #Default log type is INFO, in case invalid type is given
    else:
        logger.info(message)
        console_output = 'INFO '+message
 
    if settings.app_settings['LOG_TO_CONSOLE']:
        now = datetime.datetime.now()
        date = utils.formatDate(now)
        time = utils.formatTime(now)

        print('<'+date+' '+time+'> '+console_output)

def logError(message):
    """
    Wrapper for logEvent function, used for logging any kind of error.
    Typically only called from logTraceback function.

    Args:
        message (string): Description of events.
    """
    logEvent(message, log_type=logging.WARNING, logger=errorLogger)

def logTraceback(message, stack_traceback):
    """
    Wrapper for logEvent and logError, used when errors occur.
    Summary info is written to one file, and detailed info is written
    to another.

    Args:
        message (string): Description of events.
        stack_traceback (string): Events that occured that caused the error.
    """

    log_time = datetime.datetime.now()
    f_log_time = utils.formatDate(log_time) + ' ' + utils.formatTime(log_time)
    if not stack_traceback == '':
        stack_traceback = ''.join([ '\n<'+f_log_time+'>',
                                    '\n########################################################################################################\n',
                                    traceback.format_exc().strip(),
                                    '\n########################################################################################################\n\n',
                                  ])
        logEvent(stack_traceback, log_type=logging.INFO, logger=tracebackLogger)

    logEvent(message + ' (See \''+settings.app_settings['TRACEBACK_LOG'] + '\' at time: '+f_log_time+' for more details)', log_type=logging.ERROR, logger=errorLogger)