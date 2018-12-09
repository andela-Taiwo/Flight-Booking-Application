import pytz
from .models import Flight, Passenger
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
from django.contrib.sites.models import Site
from django.db import (
    transaction,
    IntegrityError,
    models
)


def send_flight_detail():
    site = Site.objects.first()
    passengers = Passenger.objects.filter(
        passenger_flight__author__isnull=False,
        passenger_flight__notification_sent_at__isnull=True
        ).prefetch_related('passenger_flight')
    current_time = datetime.now().replace(tzinfo=pytz.UTC)
    for passenger in passengers:
        if passenger.passenger_flight.notification_sent_at is None and \
        (passenger.passenger_flight.departure - current_time).total_seconds() <= 24*3600:
            notification_text = """Hi,
                    Here is to tell you for flight is due in the next 24 hours. Please confirm checking by clicking on the link below

                    {}/api/v1/flight/{}/confirm/

                    Have a nice day.
                    Fly-Right Admin
                    """.format(site, passenger.passenger_flight.pk)

            send_mail(
                'Confirm Flight Checkin',
                notification_text,
                settings.EMAIL_HOST_USER,
                [passenger.email],
                fail_silently=False,
            )
            with transaction.atomic():
                passenger.passenger_flight.notification_sent_at = current_time
                passenger.passenger_flight.checkin = True
                passenger.passenger_flight.save()
                passenger.save()
