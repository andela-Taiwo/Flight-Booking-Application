from settings.base import *

DEBUG = True

ALLOWED_HOSTS = [
    'localhost', '127.0.0.1',    
]

# INSTALLED_APPS += [
#     'debug_toolbar',
# ]

LOGIN_URL='http://127.0.0.1/api/v1/login/'
SITE_ID=2


# MIDDLEWARE += [
#     'debug_toolbar.middleware.DebugToolbarMiddleware',
# ]