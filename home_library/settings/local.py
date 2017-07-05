from .base import *


SECRET_KEY = '9i5igtvm5w(ajeq4$i_m(0^_p3z^yw3k1p-54ab$4k5t_8jpk='

DEBUG = True

ALLOWED_HOSTS += (
    '127.0.0.1',
    'localhost',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

MEDIA_ROOT = os.path.join(BASE_DIR, '../media')
