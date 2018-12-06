import pytz
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
    # passenger = models.ForeignKey(Passenger, related_name='passenger', on_delete=models.PROTECT)
    # user = models.ForeignKey(User, related_name='Client', on_delete=models.PROTECT)
    starting_from = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    departure = models.DateTimeField(null=True, blank=True)
    arrival = models.DateTimeField(null=True, blank=True)
    flight_type = models.IntegerField(choices=FLIGHT_TYPE, default=BUSINESS_CLASS)
    ticket_type = models.IntegerField(choices=TICKET_TYPE, default=RETURN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    checkin = models.BooleanField()


class Passenger(models.Model):
    ''' Passenger Model '''
    MALE = 0
    FEMALE = 1
    UNKNOWN = 2
    GENDER =  (
        (FEMALE, _('Female')),
        (MALE, _('Male')),
        (UNKNOWN, _('Unkonwn'))
    )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    gender = models.IntegerField(choices=GENDER)
    passport_number = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=255)
    date_of_birth = models.DateTimeField()
    contact_next_of_kin_name = models.CharField(
        max_length=255, null=True, blank=True,
        verbose_name='Name')
    contact_next_of_kin_relationship = models.CharField(
        max_length=255, null=True, blank=True,
        verbose_name='Relationship')
    contact_next_of_kin_phone = models.CharField(
        max_length=255, null=True, blank=True,
        verbose_name='Phone')
    contact_next_of_kin_mobile = models.CharField(
        max_length=255, null=True, blank=True,
        verbose_name='Mobile')
    contact_next_of_kin_email = models.CharField(
        max_length=255, null=True, blank=True,
        verbose_name='E-mail')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    flight = models.ForeignKey(Flight, related_name='flight', on_delete=models.CASCADE)
