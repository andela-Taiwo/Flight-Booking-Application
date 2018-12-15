from django.contrib.auth.models import User
from user.models import Profile
from rest_framework_jwt import utils
from django.conf import settings
from allauth.utils import get_user_model
from user.services import make_file_key
from user.models import Upload

def _create_user(self, email='johndoe@gmail.com', password='tester123'):
    user = get_user_model().objects.create(
        email=email, password=password,
        is_active=True)
    if password:
        user.set_password(password)
    else:
        user.set_unusable_password()
    user.save()
    return user
    