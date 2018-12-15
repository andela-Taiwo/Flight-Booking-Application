import pytz
from datetime import datetime, timedelta
from django.urls.exceptions import NoReverseMatch
from django.contrib.auth.models import User
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from flight.models import Flight, Passenger
from user.tests import factory as user_factory
from flight.tasks import task_notify_user, task_user_flight_detail

class TestUtils(APITestCase):
    def setUp(self):

        self.invalid_token = 'Bearer Eyhbfhebjwkfbhjbuw3hiuhufhnffjjfjk'
        self.user = user_factory._create_user(self,email='testadmin@gmail.com')
        self.flight = Flight.objects.create(
            arrival = "2019-02-01T15:11:26.319021Z",
            departure = datetime.now().replace(tzinfo=pytz.UTC)+timedelta(hours=23),
            starting_from = 'LOS',
            destination = 'LHR',
            author=self.user,
            checkin=False
        )
        self.passenger = Passenger.objects.create(
            first_name ='Jon',
            last_name= 'Snow',
            gender= 2,
            contact_next_of_kin_name='Jon Doe',
            contact_next_of_kin_relationship='brother',
            contact_next_of_kin_phone='+23480345836530398',
            passenger_flight=self.flight,
            passport_number='AO465739237',
            email='test2@gmail.com',
            phone_number='+234080535756',
            date_of_birth="2000-11-05T15:11:26.319021Z"

        )
        self.flight2 = Flight.objects.create(
            arrival = "2019-01-05T15:11:26.319021Z",
            departure = "2019-11-05T15:11:26.319021Z",
            starting_from = 'LHR',
            destination = 'MMK',
            author=self.user,
            checkin=False,
            ticket_type=1,
            flight_type=1
        )

        self.task1 = task_notify_user(self.passenger.email, self.flight.pk)
        self.task2 = task_user_flight_detail()

    def test_send_notification(self):
        self.assertEqual(self.task1, 1)

    def test_send_flight_reminder(self):
        flight = Flight.objects.get(id=self.flight.id)
        self.assertIsNot(flight.notification_sent_at, None)
