import os
from settings.base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'mydatabase',
    }
}
SECRET_KEY = os.environ.get('SECRET_KEY')