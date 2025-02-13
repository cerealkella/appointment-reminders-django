import time
import datetime
import sys
import socket
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from django.db import connections, connection
from django.db.utils import InterfaceError, OperationalError
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from reminders.models import Appointment, ValidationError


"""
Launch APScheduler
Call this from models or urls
When using with gunicorn - it's essential to launch gunicorn
with the --preload flag. This will prevent APScheduler from
launching in multiple threads. See stackoverflow for explanation:
https://stackoverflow.com/questions/16053364/make-sure-only-one-worker-launches-the-apscheduler-event-in-a-pyramid-web-app-ru
Also employing the use of a socket to ensure multiple instances of
APScheduler are not launched
"""
scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")


def dictfetchall(days_in_advance):
    "Return all rows from a cursor as a dict"
    sql = """
    SELECT DISTINCT profile.prof_c_profilenum as profile_id,
                    prof_c_ip1firstname as name,
                    sch5event_contact_cell_phone as phone_number,
                    prof_c_commpref as comm_pref,
                    profile.prof_c_ip1p_phone as home_phone,
    				profile.prof_c_ip1p_email as email,
                    sch5event_id as id,
                    sch5appt_datetime as time
    FROM   scheduling_appointment
           JOIN scheduling_event
             ON sch5appt_eventid = sch5event_id
           JOIN profile
             ON prof_c_profilenum = sch5event_profile
           join (select * from scheduling_event_task where sch5evtks_seq = 1) as sch5evtask on sch5event_id = sch5evtks_event_id
           join scheduling_task on sch5evtks_task_id = sch5task_id
            /* FILTER APPOINTMENT STATUS
            * SELECT THE MOST RECENT STATUS UPDATE
            * FROM THE SCHEDULING_APPOINTMENT_STATUS
            * TABLE USING THE MAX FUNCTION
            * THEN JOIN AGAIN - FILTER TO SCHEDULED (S)
            */
           join (select max(sch5apptstat_id) as id, sch5apptstat_apptid from scheduling_appointment_status group by sch5apptstat_apptid) as ss on ss.sch5apptstat_apptid = sch5appt_id
           join scheduling_appointment_status on sch5apptstat_id = ss.id
    WHERE  Date(sch5appt_datetime) = {}
    	   and sch5task_owner_dept in (34,47,49,50,51,55,22)
           and sch5apptstat_code = 'S'
           and sch5appt_duration > 15
    ORDER  BY sch5appt_datetime
    """
    appt_date = str(datetime.date.today() + datetime.timedelta(days=days_in_advance))
    results = {}
    try:
        cursor = connections["emr"].cursor()
        cursor.execute(sql.format("'" + appt_date + "'"))
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    except (InterfaceError, OperationalError) as e:
        print("{} - Connection unavailable, will try again later".format(e))
    finally:
        cursor.close()
        return results


@register_job(
    scheduler, "cron", hour="7", minute=45, replace_existing=True, jitter=20
)
def populate_appt_database():
    """Specify the days in advance to send out reminders"""
    reminders = (1,)
    print("{} - Scraping Database for Appointments".format(datetime.datetime.now()))
    for i in reminders:
        rows = dictfetchall(i)
        for r in rows:
            appt = Appointment.objects.all()
            if appt.filter(emr_id=r["id"], reminder_days=i):
                # print("{0}-day appointment reminder already exists for id {1}".format(i, r['id']))
                pass
            else:
                a = Appointment(
                    profile_id=r["profile_id"],
                    emr_id=r["id"],
                    name=r["name"].capitalize(),
                    time=r["time"],
                    phone_number=r["phone_number"],
                    home_phone=r["home_phone"],
                    email=r["email"],
                    comm_pref=r["comm_pref"],
                    reminder_days=i,
                )
                try:
                    a.clean()
                except ValidationError:
                    print("Appointment in the past")
                else:
                    a.save()
    return("Completed DB Scrape. {} Appointments found".format(len(rows)))


try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 47200))
except socket.error:
    print("!!!scheduler already started, DO NOTHING")
else:
    register_events(scheduler)
    scheduler.start()
    print("{0} - Scheduler started!".format(datetime.datetime.now()))

