'''
Dramatiq settings

Built a separate settings file for Dramatiq due to the issue
of APScheduler spawning and creating duplicate jobs. 
APScheduler will run multiple times via gunicorn workers,
which is problematic.
The workaround for this is to spawn APScheduler only from
dramatiq, allowing the use of multiple workers in the main
gunicorn app.

'''
from .common import *
from .local import *  # noqa

# Use DEBUG for local development
DEBUG = True

# Override Broker to run APScheduler alongside Dramatiq
SCHEDULER_AUTOSTART = True
