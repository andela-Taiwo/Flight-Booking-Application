from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger
from django.contrib.sites.models import Site
from django.conf import settings
from django.core.mail import send_mail
from celery.decorators import task
from .celery import app

from flight.utils import send_flight_detail

logger = get_task_logger(__name__)

site = Site.objects.first()

@app.task(name="send_notification_flight_reservation")
def task_notify_user(email, flight):
    logger.info("Send user's flight reservation notification")
    notification_text = """Hi,
                    This is to inform you that your flight reservation on Fly-Right was successful. 
                    You can click on the link below for the flight details.
                    {}/api/v1/flight/{}

                    Have a nice day.
                    Fly-Right Admin
                    """.format(site, flight.pk)
    send_mail(
        'Hello',
        notification_text,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )

@periodic_task(
    run_every=(crontab(minute='*')),
    name="task_user_flight_detail",
    ignore_result=True
)
def task_user_flight_detail():
    """
    Send email to notify user after reserving flight
    """
    send_flight_detail()
    logger.info("Send user's flight detail")