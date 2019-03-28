'''
Dramatiq settings

Built a separate settings file for Dramatiq due to the issue
of APScheduler spawning and creating duplicate jobs. 
'''

from .common import *
from .local import *  # noqa

# Use DEBUG for local development
DEBUG = True

# Override Broker to run APScheduler alongside Dramatiq
SCHEDULER_AUTOSTART = False
