import pytz
from datetime import datetime
from django.urls.exceptions import NoReverseMatch
from django.contrib.auth.models import User
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from user.models import Profile
from flight.models import Flight, Passenger
from user.tests import factory as user_factory
from allauth.account.models import (
    EmailAddress,
    EmailConfirmation
)
from django.core.files.uploadedfile import SimpleUploadedFile
from api.s3_services import MockStore
from allauth.utils import get_user_model

mockstore = MockStore()

class TestFlightAPI(APITestCase):

    def setUp(self):
        self.invalid_token = 'Bearer Eyhbfhebjwkfbhjbuw3hiuhufhnffjjfjk'
        self.user = user_factory._create_user(self,email='testadmin@gmail.com')
        self.date_ = datetime.now().strftime('%Y-%m-%d')
        self.flight = Flight.objects.create(
            arrival = "2019-02-01T15:11:26.319021Z",
            departure = "2019-01-31T15:11:26.319021Z",
            starting_from = 'LOS',
            destination = 'LHR',
            author=self.user,
            checkin=False
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

    def _create_login_user_with_verified_email(self, email='user@example.com', password='$testeR1234', user_status=False):
        """Tests login """
        user = get_user_model().objects.create(email=email, password=password)
        user.set_password(password)
        user.is_staff = user_status
        user.save()
        EmailAddress.objects.create(user=user,
                                    email=email,
                                    primary=True,
                                    verified=True)
        response = self.client.post(reverse('account_login'),
                                {'email': email,
                                 'password': password})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user']['email'], email)
        return response

    def _create_flight(self, requestor, data=None):
        if data is None:
            data = {
                'arrival': "2019-12-05T15:11:26.319021Z",
                'departure': "2019-11-05T15:11:26.319021Z",
                'starting_from':'LOS',
                'destination': 'HMK'
            }

        response = self.client.post(
            reverse(
                'apiv1_flight-list'
            ),
            data=data,
            HTTP_AUTHORIZATION='Bearer {}'.format(requestor.data['token']),
            format='multipart'
        )

        self.assertEqual(response.status_code, 200)
        return response.data


    def test_reserve_flight(self):
        user = self._create_login_user_with_verified_email()
        data = {
            'arrival': "2019-12-05T15:11:26.319021Z",
            'departure': "2019-11-05T15:11:26.319021Z",
            'starting_from':'LOS',
            'destination': 'HMK'
        }

        response = self.client.post(
            reverse(
                'apiv1_flight-list'
            ),
            data=data,
            HTTP_AUTHORIZATION='Bearer {}'.format(user.data['token']),
            format='multipart'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['payload'][0]['destination'], data['destination'])
        self.assertEqual(response.data['payload'][0]['author'], user.data['user']['pk'])

    def test_list_flight(self):
        user = self._create_login_user_with_verified_email()
        response = self.client.get(
            reverse(
                'apiv1_flight-list'
            ),
            data={
                "flight_type": 1,
                "ticket_type": 1
            },
            HTTP_AUTHORIZATION='Bearer {}'.format(user.data['token']),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['payload']), 1)
        self.assertEqual(response.data['payload'][0]['author'], self.user.pk)
        self.assertEqual(response.data['payload'][0]['flight_type'], 1)
        self.assertEqual(response.data['payload'][0]['ticket_type'], 1)

    def test_list_flight_users_for_a_day(self):
        user = self._create_login_user_with_verified_email()
        flight = self._create_flight(requestor=user)
        data = {
            'first_name': 'Jon',
            'last_name': 'Snow',
            'gender': 2,
            'contact_next_of_kin_name': 'Jon Doe',
            'contact_next_of_kin_relationship': 'brother',
            'contact_next_of_kin_phone ': '+23480345836530398',
            'passenger_flight': flight['payload'][0]['id'],
            'passport_number': 'AO465739237',
            'email': 'test2@gmail.com',
            'phone_number': '+234080535756',
            'date_of_birth': "2000-11-05T15:11:26.319021Z"

        }
        book_ticket = self.client.post(
            reverse(
                'apiv1_flight-book-flight'
            ),
            data=data,
            HTTP_AUTHORIZATION='Bearer {}'.format(user.data['token']),
        )
        self.assertEqual(book_ticket.status_code, 200)
        # response = self.client.get(
        #     reverse(
        #         'apiv1_flight-list-users', args=[0, self.date_]
        #     ),
        #     data={
        #         # "flight_type": 1,
        #         # "ticket_type": 1
        #     },
        #     HTTP_AUTHORIZATION='Bearer {}'.format(user.data['token']),
        # )
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(len(response.data['payload']), 1)
        # self.assertEqual(response.data['payload'][0]['author'], self.user.pk)
        # self.assertEqual(response.data['payload'][0]['flight_type'], 1)
        # self.assertEqual(response.data['payload'][0]['ticket_type'], 1)

    def test_list_flight_confirmation(self):
        user = self._create_login_user_with_verified_email()
        flight = self._create_flight(requestor=user)
        data = {
            'first_name': 'Jon',
            'last_name': 'Snow',
            'gender': 2,
            'contact_next_of_kin_name': 'Jon Doe',
            'contact_next_of_kin_relationship': 'brother',
            'contact_next_of_kin_phone ': '+23480345836530398',
            'passenger_flight': flight['payload'][0]['id'],
            'passport_number': 'AO465739237',
            'email': 'test2@gmail.com',
            'phone_number': '+234080535756',
            'date_of_birth': "2000-11-05T15:11:26.319021Z"

        }
        response = self.client.post(
            reverse(
                'apiv1_flight-book-flight'
            ),
            data=data,
            HTTP_AUTHORIZATION='Bearer {}'.format(user.data['token'])
        )
        response = self.client.put(
            reverse(
                'apiv1_flight-confirm-flight-checkin', args=[flight['payload'][0]['id']]
            ),
            data={},
            HTTP_AUTHORIZATION='Bearer {}'.format(user.data['token']),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['payload']['passenger_flight']['checkin'], True)
        self.assertEqual(response.data['payload']['email'], data['email'])

    
    def test_update_flight(self):
        user = self._create_login_user_with_verified_email()
        flight = self._create_flight(requestor=user)
        response = self.client.put(
            reverse(
                'apiv1_flight-detail', args=[flight['payload'][0]['id']]
            ),
            data={
                "flight_type": 1,
                "ticket_type": 1,
                'destination': 'NYK'
            },
            HTTP_AUTHORIZATION='Bearer {}'.format(user.data['token']),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['payload']['author'], user.data['user']['pk'])
        self.assertEqual(response.data['payload']['flight_type'], 1)
        self.assertEqual(response.data['payload']['ticket_type'], 1)
        self.assertEqual(response.data['payload']['destination'], 'NYK')


    def test_retrieve_flight(self):
        user = self._create_login_user_with_verified_email()
        flight = self._create_flight(requestor=user)
        response = self.client.get(
            reverse(
                'apiv1_flight-detail', args=[flight['payload'][0]['id']]
            ),
            data={
            },
            HTTP_AUTHORIZATION='Bearer {}'.format(user.data['token']),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['payload']['author'], user.data['user']['pk'])
        self.assertEqual(response.data['payload']['flight_type'], 0)
        self.assertEqual(response.data['payload']['ticket_type'], 0)
    
    def test_book_ticket(self):
        user = self._create_login_user_with_verified_email()
        flight = self._create_flight(requestor=user)
        data = {
            'first_name': 'Jon',
            'last_name': 'Snow',
            'gender': 2,
            'contact_next_of_kin_name': 'Jon Doe',
            'contact_next_of_kin_relationship': 'brother',
            'contact_next_of_kin_phone ': '+23480345836530398',
            'passenger_flight': flight['payload'][0]['id'],
            'passport_number': 'AO465739237',
            'email': 'test2@gmail.com',
            'phone_number': '+234080535756',
            'date_of_birth': "2000-11-05T15:11:26.319021Z"

        }
        response = self.client.post(
            reverse(
                'apiv1_flight-book-flight'
            ),
            data=data,
            HTTP_AUTHORIZATION='Bearer {}'.format(user.data['token']),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['payload'][0]['last_name'], data['last_name'])
        self.assertEqual(response.data['payload'][0]['passenger_flight']['starting_from'],
        flight['payload'][0]['starting_from']
        )
   
    def test_book_ticket_payment(self):
        user = self._create_login_user_with_verified_email()
        flight = self._create_flight(requestor=user)
        data = {
            'first_name': 'Jon',
            'last_name': 'Snow',
            'gender': 2,
            'contact_next_of_kin_name': 'Jon Doe',
            'contact_next_of_kin_relationship': 'brother',
            'contact_next_of_kin_phone ': '+23480345836530398',
            'passenger_flight': flight['payload'][0]['id'],
            'passport_number': 'AO465739237',
            'email': 'test2@gmail.com',
            'phone_number': '+234080535756',
            'date_of_birth': "2000-11-05T15:11:26.319021Z"

        }
        ticket = self.client.post(
            reverse(
                'apiv1_flight-book-flight'
            ),
            data=data,
            HTTP_AUTHORIZATION='Bearer {}'.format(user.data['token']),
        )


        self.assertEqual(ticket.status_code, 200)
        response = self.client.post(
            reverse(
                'apiv1_flight-flight-payment'
            ),
            data={
                'flight_id': flight['payload'][0]['id'],
                'token': '476598863'
            },
            HTTP_AUTHORIZATION='Bearer {}'.format(user.data['token']),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['payload'][0]['payment'], True)
        self.assertEqual(response.data['payload'][0]['price'], '100000.0000')

    
    
        
class TestFlightAPIExceptions(TestFlightAPI):
    def test_book_ticket_payment_invalid_token(self):
        user = self._create_login_user_with_verified_email()
        flight = self._create_flight(requestor=user)
        data = {
            'first_name': 'Jon',
            'last_name': 'Snow',
            'gender': 2,
            'contact_next_of_kin_name': 'Jon Doe',
            'contact_next_of_kin_relationship': 'brother',
            'contact_next_of_kin_phone ': '+23480345836530398',
            'passenger_flight': flight['payload'][0]['id'],
            'passport_number': 'AO465739237',
            'email': 'test2@gmail.com',
            'phone_number': '+234080535756',
            'date_of_birth': "2000-11-05T15:11:26.319021Z"

        }
        ticket = self.client.post(
            reverse(
                'apiv1_flight-book-flight'
            ),
            data=data,
            HTTP_AUTHORIZATION='Bearer {}'.format(user.data['token']),
        )


        self.assertEqual(ticket.status_code, 200)
        response = self.client.post(
            reverse(
                'apiv1_flight-flight-payment'
            ),
            data={
                'flight_id': flight['payload'][0]['id'],
                'token': 'badtoken'
            },
            HTTP_AUTHORIZATION='Bearer {}'.format(user.data['token']),
        )
        self.assertEqual(response.status_code, 406)
        self.assertEqual(response.data['detail'], 'Invalid token')
    

    def test_book_ticket_invalid_payload(self):
        user = self._create_login_user_with_verified_email()
        flight = self._create_flight(requestor=user)
        data = {
            'first_name': 'Jon',
            'last_name': 'Snow',
            'gender': 2,
            'contact_next_of_kin_name': 'Jon Doe',
            'contact_next_of_kin_relationship': 'brother',
            'contact_next_of_kin_phone ': '+23480345836530398',
            'passenger_flight': flight['payload'][0]['id']

        }
        response = self.client.post(
            reverse(
                'apiv1_flight-book-flight'
            ),
            data=data,
            HTTP_AUTHORIZATION='Bearer {}'.format(user.data['token']),
        )
        self.assertEqual(response.status_code, 400)

        self.assertEqual(response.data['email'][0], 'This field is required.')
        self.assertEqual(response.data['passport_number'][0], 'This field is required.')

    def test_update_invalid_flight(self):
        user = self._create_login_user_with_verified_email()
        response = self.client.put(
            reverse(
                'apiv1_flight-detail', args=['a']
            ),
            data={
                "flight_type": 1,
                "ticket_type": 1,
                'destination': 'NYK'
            },
            HTTP_AUTHORIZATION='Bearer {}'.format(user.data['token']),
        )
        self.assertEqual(response.status_code, 406)
        self.assertEqual(response.data['detail'], 'Invalid flight number')


    def test_retrieve_invalid_flight(self):
        user = self._create_login_user_with_verified_email()
        response = self.client.get(
            reverse(
                'apiv1_flight-detail', args=['a']
            ),
            data={
            },
            HTTP_AUTHORIZATION='Bearer {}'.format(user.data['token']),
        )
        self.assertEqual(response.status_code, 406)
        self.assertEqual(response.data['detail'], 'Invalid flight number')
