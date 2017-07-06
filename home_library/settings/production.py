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

AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_S3_CUSTOM_DOMAIN = '{}.s3.amazonaws.com'.format(AWS_STORAGE_BUCKET_NAME)
STATIC_URL = "https://{}/".format(AWS_S3_CUSTOM_DOMAIN)
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3BotoStorage'
