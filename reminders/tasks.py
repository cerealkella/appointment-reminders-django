from __future__ import absolute_import

import arrow
import dramatiq

from django.conf import settings
from twilio.rest import Client

from .models import Appointment
from appointments.settings.local import EMAIL_SERVER_SETTINGS, ORGANIZATION

import smtplib
import ssl
import re


def _valid_cell(appointment):
    if len(appointment.phone_number) > 5:
        return True
    else:
        return False


def _valid_home_phone(appointment):
    if len(appointment.home_phone) > 5:
        return True
    else:
        return False


def _valid_email(appointment):
    if len(appointment.email) > 5:
        if appointment.email == "decline@test.com":
            return False
        elif re.match(r"[^@]+@[^@]+\.[^@]+", appointment.email) != None:
            return True
    else:
        return False


def _send_sms_reminder(appointment, body):
    # Uses credentials from the TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN
    # environment variables
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    """Send SMS to recipient"""
    client.messages.create(
        body=body,
        to=appointment.phone_number,
        # to=ORGANIZATION["TEST_CELL_NUMBER"],
        from_=settings.TWILIO_NUMBER,
    )
    return True


def _send_email_reminder(appointment, body):
    """Send email to recipient"""
    body += "\n\nThis mailbox is not monitored, please do not reply."
    message = "Subject: {}\n\n{}".format("Your Upcoming Appt", body)
    print(EMAIL_SERVER_SETTINGS)
    print(message)

    with smtplib.SMTP(
        EMAIL_SERVER_SETTINGS["SMTP_SERVER"], EMAIL_SERVER_SETTINGS["PORT"]
    ) as server:
        server.ehlo()  # Can be omitted
        server.starttls()
        server.ehlo()  # Can be omitted
        server.login(
            EMAIL_SERVER_SETTINGS["USERNAME"], EMAIL_SERVER_SETTINGS["PASSWORD"]
        )
        result = server.sendmail(EMAIL_SERVER_SETTINGS['SENDER_EMAIL'], appointment.email, message)
        # result = server.sendmail(
        #     EMAIL_SERVER_SETTINGS["SENDER_EMAIL"], ORGANIZATION["TEST_EMAIL"], message
        # )
        server.close()
    return result


def _make_phone_call(appointment):
    """Send a voice reminder to a phone using Twilio"""

    if _valid_home_phone(appointment):
        number_to_call = appointment.home_phone
    elif _valid_cell(appointment):
        number_to_call = appointment.phone_number
    else:
        print("No valid number to call")
        return False

    # The appointment object is UTC when pulling from the database
    # need to convert to the proper timezone using code below
    utcappt = arrow.get(appointment.time)
    appointment_time = utcappt.to(appointment.time_zone)

    body = f""". . . Hello from {ORGANIZATION['NAME']}! {appointment.name} has an appointment coming up on
        {appointment_time.format('M/D')} at {appointment_time.format('h:mm a')}.
        Please call {ORGANIZATION['PHONE']} if you need to reschedule. Please arrive 15 min early to register,
        and please don't forget to bring any medications you may be taking, and your co-pay! . . . . ."""

    message = ""
    i = 0
    while i < 3:
        message += body
        i += 1

    client = Client()
    call = client.calls.create(
        # url=ORGANIZATION["SITE_BASE_URL"]
        # + "appointments/xml/{}/".format(appointment.id),
        twiml=f"""<Response><Say>{message}</Say></Response>""",
        to=number_to_call,
        # to=ORGANIZATION["TEST_HOME_PHONE"],
        # Outbound Caller ID, if different than TWILIO #, must be verified w/twilio
        # from_=settings.TWILIO_NUMBER,
        from_=ORGANIZATION['PHONE']
    )
    print(call.sid)
    return True


@dramatiq.actor(max_retries=5, min_backoff=20000, max_backoff=21600000)
def send_reminder(appointment_id):
    """Send a reminder!"""
    # Get our appointment from the database
    try:
        appointment = Appointment.objects.get(pk=appointment_id)
    except Appointment.DoesNotExist:
        # The appointment we were trying to remind someone about
        # has been deleted, so we don't need to do anything
        return

    # The appointment object is UTC when pulling from the database
    # need to convert to the proper timezone using code below
    utcappt = arrow.get(appointment.time)
    appointment_time = utcappt.to(appointment.time_zone)

    body = """\n
        {0}- Hello from {1}! You have an appt coming up on {2} at {3}.
        Please call {4} if you need to reschedule. Be here to register 15 min early & don't forget your home meds & co-pay!
        """.format(
        appointment.name,
        ORGANIZATION["NAME"],
        appointment_time.format("M/D"),
        appointment_time.format("h:mm a"),
        ORGANIZATION["PHONE"],
    )

    print(appointment)

    if appointment.comm_pref == "":
        """No appointment preference provided"""
        if _valid_cell(appointment):
            body += " Info & forms can be found here: {0}".format(
                ORGANIZATION["WEB_RESOURCE"]
            )
            _send_sms_reminder(appointment, body)
            return True
        elif _valid_email(appointment):
            body += " Information and forms can be found here: {0}".format(
                ORGANIZATION["WEB_RESOURCE"]
            )
            _send_email_reminder(appointment, body)
            return True
        elif _valid_home_phone(appointment):
            _make_phone_call(appointment)
            return True
        return False

    elif appointment.comm_pref == "M":
        """Send SMS"""
        if _valid_cell(appointment):
            body += " Information and forms can be found here: {0}".format(
                ORGANIZATION["WEB_RESOURCE"]
            )
            _send_sms_reminder(appointment, body)
            return True
        return False

    elif appointment.comm_pref == "E":
        if _valid_email(appointment):
            _send_email_reminder(appointment, body)
            return True
        return False

    else:  # appointment.comm_pref == 'P'
        # validity checking done in phone call function
        return _make_phone_call(appointment)
