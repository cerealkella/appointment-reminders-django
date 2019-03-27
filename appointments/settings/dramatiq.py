'''
Dramatiq settings

'''
from .common import *
from .local import *  # noqa

# Use DEBUG for local development
DEBUG = True

# Override Broker to not run APScheduler
# SCHEDULER_AUTOSTART = False
DRAMATIQ_BROKER["LOAD_APSCHEDULER"] = False