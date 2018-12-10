from django.db import models
from dateutil.parser import parse
from rest_framework import serializers
from .models import (
  Flight, Passenger
)
from user.serializers import UserSerializer
from user.models import Profile

class CreateFlightSerializer(serializers.ModelSerializer):

    ''' Serializer for creating a flight'''
    checkin = serializers.BooleanField(required=False, default=False)
    class Meta:
        model = Flight
        fields = [
            "id",
            "departure",
            "arrival",
            "starting_from",
            "destination", 
            "checkin"
        ]

    def validate_departure(self, departure):
        if (self.initial_data.get('arrival', None) == None and
                self.partial is True):
            arrival = self.instance.arrival
        else:
            arrival = self.initial_data.get('arrival', 0)
        try:
            if parse(arrival) >= departure:
                return departure
            raise serializers.ValidationError(
                'Departure Date appears after Arrival date.'
            )
        except ValueError:
            return departure

    def validate_arrival(self, arrival):
        if (self.initial_data.get('departure', None) == None and
                self.partial is True):
            departure = self.instance.departure
        else:
            departure = self.initial_data.get('departure')
        try:
            if arrival >= parse(departure):
                return arrival
            raise serializers.ValidationError(
                'End Date appears before Start date.'
            )
        except ValueError:
            return arrival

class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ('__all__')

class CreateBookFlightSerializer(serializers.ModelSerializer):  
    class Meta:
        model = Passenger
        fields = [
            'last_name',
            'first_name',
            'gender',
            'email',
            'passport_number',
            'phone_number',
            'date_of_birth',
            'contact_next_of_kin_name',
            'contact_next_of_kin_relationship',
            'contact_next_of_kin_mobile',
            'passenger_flight',
        ]
    
class BookFlightSerializer(serializers.ModelSerializer):
    passenger_flight = FlightSerializer(read_only=True)
    
    class Meta:
        model = Passenger
        fields = ('__all__') 