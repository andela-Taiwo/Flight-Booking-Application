import os
from settings.base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME':  ':memory:',
    }
}

SECRET_KEY = os.environ.get('SECRET_KEY')
SITE_ID = 1