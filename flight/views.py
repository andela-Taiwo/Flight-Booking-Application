from django.shortcuts import render
from rest_framework import (
    viewsets,
    decorators
)
from rest_framework.exceptions import APIException
from .serializers import (
    FlightSerializer,
    BookFlightSerializer
)
from rest_framework import authentication, permissions
from api.response import FlightBoookingAPIResponse
import flight.services as flight_services


# Create your views here.
class FlightViewSet(viewsets.ViewSet):

    def list(self, request):
        ''' List and flter the flights '''
        flights = flight_services.filter_flight(
            requestor=request.user,
            query_params=request.query_params
        )
        return FlightBoookingAPIResponse(
            FlightSerializer(flights, many=True).data
        )

    def update(self, request, *args, **kwargs):
        ''' Update a single flight '''
        try:
            flight_id = int(kwargs.get('pk'))
        except ValueError as e:
            raise APIException(detail='Invalid flight number')

        flight = flight_services.update_flight(
            requestor=request.user,
            data=request.data,
            flight_id=kwargs.get('pk')
        )

    def retrieve(self, request, *args, **kwargs):
        ''' Retrieve a flight'''
        try:
            flight_id = int(kwargs.get('pk'))
        except ValueError as e:
            raise APIException(detail='Invalid flight number')
        
        flight = flight_services.retrieve_flight(
            requestor=request.user,
            flight_id=kwargs.get('pk')
        )

        return FlightBoookingAPIResponse(
            FlightSerializer(
                flight
            ).data
        )

    def create(self, request, *args, **kwargs):
        ''' Create a single flight'''
        flight = flight_services.create_flight(
            data=request.data,
            requestor=request.user
        )
        return FlightBoookingAPIResponse(
            FlightSerializer(flight, many=True).data
        ) 
    @decorators.action(methods=['post'], detail=False, url_path='book')
    def book_flight(self, request, *args, **kwargs):
        booked_flight = flight_services.book_ticket(
            requestor=request.user,
            data=request.data,
        )
        return FlightBoookingAPIResponse(
            BookFlightSerializer(booked_flight, many=True).data
        )

    @decorators.action(methods=['put'], detail=False, url_path='(?P<flight_pk>\d+)/confirm')
    def confirm_flight_checkin(self, request, *args, **kwargs):
        confirmed_flight = flight_services.confirm_checkin(
            requestor=request.user,
            flight_id=kwargs.get('flight_pk')
        )
        return FlightBoookingAPIResponse(
            BookFlightSerializer(confirmed_flight).data
        )