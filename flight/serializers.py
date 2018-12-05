from django.db import models
from dateutil.parser import parse
from rest_framework import serializers
from .models import (
  Flight, Passenger
)
from user.serializers import UserSerializer
from user.models import Profile

class FlightSerializer(serializers.ModelSerializer):

    class Meta:
        model = Flight
        fields = ('__all__')


class BookFlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = ('__all__')
        