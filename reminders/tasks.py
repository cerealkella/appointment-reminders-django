from __future__ import absolute_import

import arrow
import dramatiq

from django.conf import settings
from twilio.rest import Client

from .models import Appointment
from appointments.settings.local import EMAIL_SERVER_SETTINGS, ORGANIZATION

import smtplib
import ssl


@dramatiq.actor
def send_reminder(appointment_id):
    """Send a reminder to a phone using Twilio SMS"""
    # Get our appointment from the database
    try:
        appointment = Appointment.objects.get(pk=appointment_id)
    except Appointment.DoesNotExist:
        # The appointment we were trying to remind someone about
        # has been deleted, so we don't need to do anything
        return

    appointment_time = arrow.get(appointment.time, appointment.time_zone.zone)
    body = '''\n
        {0}- Hello from {1}! You have an appointment coming up on {2} at {3}.
        If you can't make it, please call {4} to reschedule.
        '''.format(
        appointment.name,
        ORGANIZATION['NAME'],
        appointment_time.format('M/D'),
        appointment_time.format('h:mm a'),
        ORGANIZATION['PHONE']
    )

    if appointment.comm_pref == 'M':
        # Uses credentials from the TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN
        # environment variables
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        '''Send SMS to recipient'''
        client.messages.create(
            body=body,
            to=appointment.phone_number,
            from_=settings.TWILIO_NUMBER,
        )
        
    elif appointment.comm_pref == 'E':
        """Send email to recipient"""
        body += "\n\nThis mailbox is not monitored, please do not reply."
        message = 'Subject: {}\n\n{}'.format("Your Upcoming Appt", body)
        print(EMAIL_SERVER_SETTINGS)
        print(message)

        with smtplib.SMTP(EMAIL_SERVER_SETTINGS['SMTP_SERVER'],EMAIL_SERVER_SETTINGS['PORT']) as server:
            server.ehlo()  # Can be omitted
            server.starttls()
            server.ehlo()  # Can be omitted
            server.login(EMAIL_SERVER_SETTINGS['USERNAME'], EMAIL_SERVER_SETTINGS['PASSWORD'])
            result = server.sendmail(EMAIL_SERVER_SETTINGS['SENDER_EMAIL'], appointment.email, message)
            server.close()
        return result
    else:
        """Send a voice reminder to a phone using Twilio"""
        client = Client()
        call = client.calls.create(
                            url='http://demo.twilio.com/docs/voice.xml',
                            to=appointment.home_phone,
                            from_=settings.TWILIO_NUMBER,
                        )
        print(call.sid)
        return call.sid