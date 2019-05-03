import os
from settings.base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME':  ':mysqlite:',
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'circleci_test',
#         'USER': 'postgres',
#         'PASSWORD': 'root',
#         'HOST': 'localhost',
#         'PORT': '',
#     }
# }

AUTH_USER_MODEL = 'user.User'
SECRET_KEY = os.environ.get('SECRET_KEY')
SITE_ID = 1