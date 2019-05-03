import pytz
import json
import random
from datetime import datetime, timedelta
from rest_framework.generics import get_object_or_404
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework.exceptions import APIException
from rest_framework import exceptions
from user.serializers import UserSerializer
from flight.models import (
  Flight, Passenger
)
from django.db import (
    transaction,
    IntegrityError,
    models
)
from .serializers import (
    CreateFlightSerializer,
    FlightSerializer,
    BookFlightSerializer,
    CreateBookFlightSerializer
    )
from flight.tasks import task_notify_user
from paystackapi.transaction import Transaction


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

def deserialize_flight(*, action='create', data, serializer_class, flight, requestor):
    ''' deserialize a flight before creating or updating'''
    assert action == 'create' or action == 'update'
    serializer = serializer_class(
        instance=flight,
        partial=(action == 'update'),
        data=data
    )
    serializer.is_valid(raise_exception=True)

    validated_data = serializer.validated_data
    if action == 'create':
        validated_data.pop('checkin', None)
        validated_data.pop('author', None)
        validated_data['author'] = requestor
        validated_data['checkin'] = False

    for name, value in validated_data.items():
        setattr(flight, name, value)

    return flight
        

def create_flight(requestor, data):
    ''' Create a flight '''
    assert(isinstance(data, list) or isinstance(data, dict)) 
    if isinstance(data, dict):
        data = [data]
    flights = []
    for dt in data:
        flight = Flight()
        data_info = dt.copy()
        flight = deserialize_flight(
            data=data_info,
            serializer_class=CreateFlightSerializer,
            flight=flight,
            requestor=requestor
        )
        with transaction.atomic():
            flight.save()
            flights.append(flight)
    return  flights

def list_users(requestor, query_params, day, type):
    ''' List users for a flight in a given day'''
    date_ = day.split('-')
    today = datetime.now().replace(tzinfo=pytz.UTC)
    try:
        year = int(date_[0])
        month = int(date_[1])
        day = int(date_[2])
        today = datetime(year=year, month=month, day=day, hour=0, minute=0, second=0).replace(tzinfo=pytz.UTC)
    except:
        raise APIException(detail='Provide proper date')
    today = datetime(year=year, month=month, day=day, hour=0, minute=0, second=0).replace(tzinfo=pytz.UTC)
    flights = Flight.objects.filter(
        departure__gte=today, flight_type=type, author__isnull=False, departure__lt=today+timedelta(hours=24)
        ).select_related('author').distinct('author')
    
    total_users = flights.count()
    flight_users = []
    for flight in flights:
        flight_users.append(flight.author)
    return {
        "users":  UserSerializer(flight_users, many=True).data,
        "total_count": total_users
        }

def filter_flight(requestor, query_params):
    '''Filter flight'''
    filter = {}
    
    if 'flight_type' in query_params:
        flight_type = json.loads(query_params.get('flight_type'))
        if isinstance(flight_type, list):
            filter['flight_type'] = flight_type
        elif isinstance(flight_type, int):
            filter['flight_type'] = [flight_type]
        else:
            raise APIException()
    
    if 'ticket_type' in query_params:
        ticket_type = json.loads(query_params.get('ticket_type'))
        if isinstance(ticket_type, list):
            filter['ticket_type'] = ticket_type
        elif isinstance(ticket_type, int):
            filter['ticket_type'] = [ticket_type]
        else:
            raise APIException()

    queryset = Flight.objects.filter(
        created_at__isnull=False
    ).order_by('-created_at')
   
 
    if 'ticket_type' in filter:
        ticket_type = filter['ticket_type']
        include, exclude = _split_choices_int(ticket_type)
        if len(include) != 0:
            queryset = queryset.filter(ticket_type__in=include)
        if len(exclude) != 0:
            queryset = queryset.exclude(ticket_type__in=exclude)

    if 'flight_type' in filter:
        flight_type = filter['flight_type']
        include, exclude = _split_choices_int(flight_type)
        if len(include) != 0:
 
            queryset = queryset.filter(flight_type__in=include)
        if len(exclude) != 0:
            queryset = queryset.exclude(flight_type__in=exclude)

    return queryset

def retrieve_flight(requestor, flight_id):
    ''' Retrieve a single flight '''
    flight = get_object_or_404(Flight, id=flight_id)
    if requestor.is_staff or requestor == flight.author:
        return flight
    return exceptions.PermissionDenied(detail='Not authorized.')

def update_flight(requestor, flight_id, data):
    '''Update a single flight '''
    flight = retrieve_flight(requestor, flight_id)
    if requestor.is_staff or requestor == flight.author:
        data_info = data.copy() 
        updated_flight = deserialize_flight(
            data=data_info,
            serializer_class=FlightSerializer,
            flight=flight,
            action='update',
            requestor=requestor
        )
        with transaction.atomic():
            updated_flight.save()
        return updated_flight
    else:
        raise exceptions.PermissionDenied()


def deserialize_ticket(*, action='create', data, serializer_class, ticket):
    ''' deserialize a flight before creating or updating'''
    assert action == 'create' or action == 'update'
    serializer = serializer_class(
        instance=ticket,
        partial=(action == 'update'),
        data=data
    )
    serializer.is_valid(raise_exception=True)

    validated_data = serializer.validated_data

    for name, value in validated_data.items():
        setattr(ticket, name, value)

    return ticket

def book_ticket(requestor, data):
    assert(isinstance(data, list) or isinstance(data, dict)) 
    if isinstance(data, dict):
        data = [data]
    data_info = data.copy() 
    booked_flight = []
    for dt in data_info:
        ticket = Passenger()
        flight = retrieve_flight(requestor, dt.get('passenger_flight'))
        if requestor != flight.author and not requestor.is_staff:
            raise exceptions.PermissionDenied('Not authorized.')
        if flight:
            serializer = deserialize_ticket(
                data=dt, 
                serializer_class=CreateBookFlightSerializer,
                ticket=ticket
            )
            with transaction.atomic():
                serializer.save()
                booked_flight.append(serializer)
            task_notify_user.delay(dt.get('email'), flight.id)
    return booked_flight

def retrieve_passenger(requestor, flight_id):
    passenger = Passenger.objects.filter(passenger_flight=flight_id).first()
    return passenger

def confirm_checkin(requestor, flight_id):
    passenger = retrieve_passenger(requestor, flight_id)
    # if passenger == requestor:
    if passenger.passenger_flight.checkin == False:
        passenger.passenger_flight.checkin = True

        with transaction.atomic():
            passenger.save()
    
    return passenger
    # raise exceptions.PermissionDenied(detail='Not your flight')

    
def ticket_payment(requestor, data):
    assert(isinstance(data, list) or isinstance(data, dict)) 
    if isinstance(data, dict):
        data = [data]
    price = 0
    flights = []
    for dt in data:
        flight = retrieve_flight(requestor, dt.get('flight_id'))
        if flight.flight_type == Flight.BUSINESS_CLASS:
            price = 100000
        elif flight.flight_type == Flight.FIRST_CLASS:
            price = 200000
        else:
            raise exceptions.NotAcceptable(detail='Not a valid flight type')
        token = ['476598863', '454734423', '548893903']
        if dt.get('token') not in token:
            raise exceptions.NotAcceptable(detail='Invalid token')

        # if dt.get('token') in token:
        with transaction.atomic():
            # response = Transaction.charge_token(reference='reference',
            #                             token='token', email='email',
            #                             amount='amount')
            flight.payment = True
            flight.price = price
            flight.charge_id = random.randrange(1, 10000)
            flight.save()
        
        flights.append(flight)         
    return flights
