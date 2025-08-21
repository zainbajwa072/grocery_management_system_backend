"""
Development settings for grocery management system.
"""
from .base import *
from decouple import config

DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,*').split(',')

# Database - Use PostgreSQL if available, fallback to SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Try PostgreSQL if configured
try:
    if config('DATABASE_URL', default=None):
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': config('DB_NAME', default='grocery_db'),
                'USER': config('DB_USER', default='grocery_user'),
                'PASSWORD': config('DB_PASSWORD', default='grocery_pass'),
                'HOST': config('DB_HOST', default='localhost'),
                'PORT': config('DB_PORT', default='5432'),
            }
        }
except:
    # Fallback to SQLite if PostgreSQL not available
    pass

# Neo4j Configuration
NEO4J_URI = config('NEO4J_URI', default='bolt://localhost:7687')
NEO4J_USER = config('NEO4J_USER', default='neo4j')
NEO4J_PASSWORD = config('NEO4J_PASSWORD', default='password123')


# Development-specific settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

