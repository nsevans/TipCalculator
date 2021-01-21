ALLOWED_FILE_EXTENSIONS = {'pdf'}

def is_allowed_file(filename):
    """
    Check to see if given file is an allowed file for this program.

    Args:
        filename (string): path and name of file.

    Returns:
        bool: True if file is an allowed type.
    """
    # Make sure file has a file type, and check what file type it is
    return '.' in filename and filename.split('.')[-1].lower() in ALLOWED_FILE_EXTENSIONS

def formatTime(now):
    """
    Format the time with zero padding and micro seconds.
    Format: HH:MM:SS,mm

    Args:
        now (datetime.datetime): The current time.

    Returns:
        string: Formatted time to show hours minutes seconds and microseconds.
    """
    # Get hours, minutes and seconds with 0 padding, and microseconds with at most 3 positions
    hour = '0'+str(now.hour) if now.hour < 10 else str(now.hour)
    minute = '0'+str(now.minute) if now.minute < 10 else str(now.minute)
    second = '0'+str(now.second) if now.second < 10 else str(now.second)
    micro = str(round(now.microsecond, 3))

    return hour+':'+minute+':'+second+'.'+micro


def formatDate(now):
    """
    Format the date with zero padding.
    Format: YY-MM-DD

    Args:
        now (datetime.datetime): The current time.

    Returns:
        string: Formatted time to show Year month and day.
    """
    # Get month and day with 0 padding
    month = '0'+str(now.month) if now.month < 10 else str(now.month)
    day = '0'+str(now.day) if now.day < 10 else str(now.day)

    return str(now.year)+'-'+month+'-'+day