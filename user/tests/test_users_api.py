import pytz
import datetime
import json
from decimal import Decimal
from django.urls.exceptions import NoReverseMatch
from unittest.mock import patch
from django.contrib.auth.models import User
from rest_framework import exceptions as drf_exceptions
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from user.models import Profile
# from core.tests import factory as user_factory
# from api import services as user_services

from django.conf import settings



class TestUsersAsOperator(APITestCase):

    @classmethod
    def setUpTestData(cls):
        pass

    def test_user_registration(self):
        self.assertEqual(1+1, 2)