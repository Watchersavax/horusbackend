from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent 
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'twitter_tracker',
    "django_celery_beat",
    
]
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],  # Ensure templates folder exists
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

SECRET_KEY = 'Q_xVSDKQDDuqQLSXZo_EfXibkA9Iwnb2PMcq_TJaBNyqwSGrexrG-sGLcY1xvi6PpzI'

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]



ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
DEBUG = True


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
     'corsheaders.middleware.CorsMiddleware',  # Enable CORS
]
# MIDDLEWARE = [
#     'django.middleware.security.SecurityMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',

#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
# ]


CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Adjust for your frontend URL
]
ROOT_URLCONF = 'horus_backend.urls'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # ✅ Default SQLite
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Twitter API Keys (Replace with real values)
TWITTER_API_KEY = "Fw3BnkZUX7Hy9vi6KgUba7FJC"
TWITTER_API_SECRET = "snlzBoZnWPuecx6cDwQH2p1AfGZmluneze620hGinZ08cNxXiO"
TWITTER_BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAGLlzwEAAAAAaxUO5eQZYijo9LIPB3ev0aJl6oY%3Devc5ECg595S3KwxqXkw4heK1W2Cr9hkSYUfFR9KbbEu1WxX70E"

# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
