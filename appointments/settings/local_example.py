'''
Local settings

- Run in Debug mode
'''

from .common import *  # noqa

# Use DEBUG for local development
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        },

    'emr': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'emr',
        'USER': 'username',
        'PASSWORD': 'SUPERSECRETP@SSW0RD!',
        'HOST': '127.0.0.1',
        'PORT': '5432',
        }
}

EMAIL_SERVER_SETTINGS = {
    'PORT': 587,
    'SMTP_SERVER': "mail.test.com",
    'USERNAME': "reminderguy",
    'SENDER_EMAIL': 'reminderguy@test.com',
    'PASSWORD': 'p@ssw0rd',
}

ORGANIZATION = {
    'NAME': 'ACME, Inc',
    'PHONE': '555-867-5309',
    'WEB_RESOURCE': 'https://www.acme.inc/billing-insurance/',
    'SITE_BASE_URL': 'acme.inc',
    'TEST_CELL_NUMBER': '5556667777',
    'TEST_HOME_PHONE': '5555555555',
    'TEST_EMAIL': 'appts@mailinator.com',
}