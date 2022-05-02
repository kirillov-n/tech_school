"""
Django settings for tech_school_backend project.

Generated by 'django-admin startproject' using Django 3.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-kszi0n92%ihkc)0-pac^p&_=(z^w1&v244!8ov6ecf8g8r%bjd'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tech_school_app',
    'workersdb_app',
    'planning_app',
    'accounting_app',
    'docs_app',
    'ejournal_app',
    'survey_app',
    'hours_app',
    'dashboard_app',
    'export',
    'djoser',
    'rest_framework',
    'corsheaders',
    'crispy_forms',
    'django_extensions',
    'django_plotly_dash.apps.DjangoPlotlyDashConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'tech_school_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'hours_app/templates/',
            'workersdb_app/templates/',
            'ejournal_app/templates/',
            'planning_app/templates/',
            'survey_app/templates',
            'tech_school_app/templates',
            'dashboard_app/templates',
        ],
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

WSGI_APPLICATION = 'tech_school_backend.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tech_school_db',
        "USER": "admin",
        "PASSWORD": "admin",
        "HOST": "127.0.0.1",  # set in docker-compose.yml
        "PORT": 5432,  # default postgres port
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

CORS_ALLOWED_ORIGINS = [
    "https://example.com",
    "https://sub.example.com",
    "http://localhost:8080",
    "http://127.0.0.1:9000"
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication"
    ]
}

SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('JWT',),
}

X_FRAME_OPTIONS = 'SAMEORIGIN'

JAZZMIN_SETTINGS = {
    "custom_links": {
        "tech_school_app": [
            {"name": "Учёт часов (группа, месяц)", "url": "admin:hours_view", "icon": "fas fa-box-open"},
            {"name": "Учёт часов (год)", "url": "admin:hoursyear_view", "icon": "fas fa-box-open"},
            {"name": "Средние баллы и посещаемость", "url": "admin:ejournal_view", "icon": "fas fa-box-open"},
            {"name": "Карточки занятий", "url": "admin:classes_view", "icon": "fas fa-box-open"},
            {"name": "Календарный план (таблица)", "url": "admin:calendarplan_view", "icon": "fas fa-box-open"},
            {"name": "Учебный план (таблица)", "url": "admin:trainingplan_view", "icon": "fas fa-box-open"},
            {"name": "Расчёт зарплаты", "url": "admin:salarycount_view", "icon": "fas fa-box-open"},
            {"name": "Расчёт стипендии", "url": "admin:scholarshipcount_view", "icon": "fas fa-box-open"},
            {"name": "Производственный календарь (календарь)", "url": "admin:workingdates_view", "icon": "fas fa-calendar"},
        ],
        "survey_app": [
            {"name": "Результаты опросов", "url": "admin:surveyresults_view", "icon": "fas fa-poll-h"},
        ]
    },
    "topmenu_links": [
            {"name": "Дашборд", "url": "/dashboard/"},
    ]
}

JAZZMIN_UI_TWEAKS = {
    "theme": "flatly",
    # "dark_mode_theme": "darkly",
}


# MEDIA SECTION
MEDIA_ROOT = "media"
MEDIA_URL = "/media/"

# mailing

EMAIL_HOST = 'smtp.mail.ru'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'tech_sch@mail.ru'
EMAIL_HOST_PASSWORD = 'hcshcet1'
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True

# forms custom

CRISPY_TEMPLATE_PACK = 'bootstrap4'

GRAPH_MODELS = {
    'all_applications': True,
    'group_models': True,
}
