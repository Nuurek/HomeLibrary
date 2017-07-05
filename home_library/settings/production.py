from .base import *
import dj_database_url


SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = bool(os.environ.get('DEBUG'))

ALLOWED_HOSTS += (
    'ai-home-library.herokuapp.com',
)

database_from_env = dj_database_url.config(conn_max_age=500)
DATABASES = {
    'default': database_from_env
}

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
