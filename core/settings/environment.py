from pathlib import Path
from decouple import config, Csv
import stripe

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# Google api KEY
GOOGLE_BOOKS_API_KEY = config('GOOGLE_BOOKS_API_KEY')

# Stripe
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY')
stripe.api_key = STRIPE_SECRET_KEY
STRIPE_PUBLISHABLE_KEY = config('STRIPE_PUBLISHABLE_KEY')



# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost', cast=Csv())

CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='', cast=Csv())

ROOT_URLCONF = 'core.urls'

WSGI_APPLICATION = 'core.wsgi.application'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

