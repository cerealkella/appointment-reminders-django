'''
Dramatiq settings

'''
from .common import *
from .local import *  # noqa

# Use DEBUG for local development
DEBUG = True

# Override Autostart to not run APScheduler
SCHEDULER_AUTOSTART = False
