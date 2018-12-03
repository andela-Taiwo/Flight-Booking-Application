from django.db import models
from django.utils.translation import ugettext_lazy as _
from user.models import User

# Create your models here.


class Flight(models.Model):
    ''' Flight Model '''

    BUSINESS_CLASS = 0
    FIRST_CLASS = 1
    FLIGHT_TYPE = (
        (BUSINESS_CLASS, _('Business class')),
        (FIRST_CLASS, _('First class'))
    )


    RETURN = 0
    ONE_WAY = 1
    TICKET_TYPE = (
        (RETURN, _('Return ticket')),
        (ONE_WAY, _('One way'))
    )
    passenger = models.ForeignKey(User, related_name='passenger', on_delete=models.PROTECT)
    starting_from = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    departure = models.DateTimeField(null=True, blank=True)
    arrival = models.DateTimeField(null=True, blank=True)
    flight_type = models.IntegerField(choices=FLIGHT_TYPE, default=BUSINESS_CLASS)
    ticket_type = models.IntegerField(choices=TICKET_TYPE, default=RETURN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    checkin = models.BooleanField()
    