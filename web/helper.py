import os
import getpass
from utils import printColoured
from authentication import Authentication

def doAuthentication():
    """
    Method use to do authentication of the user.

    Returns
    -------
    session: session
        Session object to authenticate the request.
    """
    printColoured(f"[INFO]: Authentication going on for user {getpass.getuser()} ...", "green")
    auth = Authentication(maxRedirects=20)
    auth.sentryAuthentication()
    printColoured("[INFO]: Sentry authentication done !!", "green")
    auth.midwayAuthentication()
    printColoured("[INFO]: Midway authentication done !!", "green")
    return auth.session

def createLocalDirectory(dirName):
    """
    Method use to create local directory.

    Parameters
    ----------
    dirName: str
        Name of the local directory.
    """
    if not os.path.exists(dirName):
        os.makedirs(dirName)
        printColoured(f'[INFO]: Created new local directory {dirName}.', "green")
    else:
        printColoured(f'[WARN]: Local directory {dirName} already exists.', "yellow")