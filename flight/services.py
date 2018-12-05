import json
from rest_framework.generics import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.exceptions import APIException
from .models import (
  Flight, Passenger
)
from django.db import (
    transaction,
    IntegrityError,
    models
)
from .serializers import (
    FlightSerializer,
    BookFlightSerializer
    )


def _split_choices_int(choices):
    assert(isinstance(choices, list))
    include = []
    exclude = []
    for t in choices:
        try:
            t = int(t)
            if t < 0:
                exclude.append(-t)
            else:
                include.append(t)
        except:
            pass

    return include, exclude

def deserialize_flight(*, action='create', data, serializer_class, flight):
    ''' deserialize a flight before creating or updating'''
    assert action == 'create' or action == 'update'
    serializer = serializer_class(
        instance=flight,
        partial=(action == 'update'),
        data=data
    )
    serializer.is_valid(raise_exception=True)

    validated_data = serializer.validated_data

    for name, value in validated_data.items():
        setattr(flight, name, value)

    return flight
        

def create_flight(requestor, data):
    ''' Create a flight '''

    flight = Flight()
    data_info = data.copy()
    flight = deserialize_flight(
        data=data_info,
        serializer_class=FlightSerializer,
        flight=flight
    )
    with transaction.atomic():
        flight.save()
    return  flight


def filter_flight(requestor, query_params):
    '''Filter flight'''
    # permissions = user_roles.UserPermissions(requestor, 'ticket')
    # permissions.check('filter')
    filter = {}
    if 'checkin' in query_params:
        checkin_flights = json.loads(query_params.get('checkin'))
        if isinstance(checkin_flights, list):
            filter['checkin'] = checkin_flights
        elif isinstance(checkin_flights, int):
            filter['level'] = [checkin_flights]
        # else:
        #     raise api_exceptions.BadRequest()

    if 'destination' in query_params:
        flight_destination = json.loads(query_params.get('destination'))
        if isinstance(flight_destination, list):
            filter['destination'] = flight_destination
        elif isinstance(flight_destination, int):
            filter['destination'] = [flight_destination]
        # else:
        #     raise api_exceptions.BadRequest()

    if 'starting_from' in query_params:
        flight_start = json.loads(query_params.get('starting_from'))
        if isinstance(flight_start, list):
            filter['starting_from'] = flight_start
        elif isinstance(flight_start, int):
            filter['starting_from'] = [flight_start]
        # else:
        #     raise api_exceptions.BadRequest()
    
    if 'flight_type' in query_params:
        flight_type = json.loads(query_params.get('flight_type'))
        if isinstance(flight_type, list):
            filter['flight_type'] = flight_type
        elif isinstance(flight_type, int):
            filter['flight_type'] = [flight_type]
        # else:
        #     raise api_exceptions.BadRequest()
    
    if 'ticket_type' in query_params:
        ticket_type = json.loads(query_params.get('ticket_type'))
        if isinstance(ticket_type, list):
            filter['ticket_type'] = ticket_type
        elif isinstance(ticket_type, int):
            filter['ticket_type'] = [ticket_type]
        # else:
        #     raise api_exceptions.BadRequest()

    queryset = Flight.objects.filter(
        created_at__isnull=False
    )
    if 'checkin' in filter:
        flight_checkin = filter['checkin']
        include, exclude = _split_choices_int(flight_checkin)
        if len(include) != 0:
            queryset = queryset.filter(level__in=include)
        if len(exclude) != 0:
            queryset = queryset.exclude(level__in=exclude)
 
    if 'ticket_type' in filter:
        ticket_type = filter['ticket_type']
        include, exclude = _split_choices_int(ticket_type)
        if len(include) != 0:
            queryset = queryset.filter(language__in=include)
        if len(exclude) != 0:
            queryset = queryset.exclude(language__in=exclude)

    if 'flight_type' in filter:
        media_type = filter['flight_type']
        include, exclude = _split_choices_int(media_type)
        if len(include) != 0:
 
            queryset = queryset.filter(type__in=include)
        if len(exclude) != 0:
            queryset = queryset.exclude(type__in=exclude)
    
    if 'destination' in filter:
        flight_destination = filter['destination']
        include, exclude = _split_choices_int(flight_destination)
        if len(include) != 0:
 
            queryset = queryset.filter(type__in=include)
        if len(exclude) != 0:
            queryset = queryset.exclude(type__in=exclude)
    
    if 'starting_from' in filter:
        flight_start = filter['starting_from']
        include, exclude = _split_choices_int(flight_start)
        if len(include) != 0:
 
            queryset = queryset.filter(type__in=include)
        if len(exclude) != 0:
            queryset = queryset.exclude(type__in=exclude)

    return queryset

def retrieve_flight(requestor, flight_id):
    ''' Retrieve a single flight '''
    # if requestor.is_staff or requestor == author:
    flight = get_object_or_404(Flight, id=flight_id)
    return flight

def update_flight(requestor, flight_id, data):
    '''Update a single flight '''
    # if requestor.is_staff or requestor == author:
    data_info = data.copy() 
    flight = retrieve_flight(requestor, flight_id)
    updated_flight = deserialize_flight(
        data=data_info,
        serializer_class=FlightSerializer,
        flight=flight,
        action='update'
    )
    with transaction.atomic():
        updated_flight.save()
    return updated_flight

def book_flight(requestor, flight_id, data):
    # if requestor.is_staff or requestor == author:
    data_info = data.copy() 
    flight = retrieve_flight(requestor, flight_id)

    if flight:
        data_info['flight'] = flight
        serializer = BookFlightSerializer(data=data_info)
        with transaction.atomic():
            serializer.is_valid(raise_exception=True)
            serializer.save()
