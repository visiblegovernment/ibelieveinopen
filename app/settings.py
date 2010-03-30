# Django settings for changecongress project.
import os


ADMINS = (
     ('Jennifer Bell', 'jenniferlianne@yahoo.ca'),
)

MANAGERS = ADMINS

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin_media/'


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)


ROOT_URLCONF = 'app.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_PATH, 'templates'),
    os.path.join(PROJECT_PATH, 'track/templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'app.context_processors.misc',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.syndication',
    'registration',
    'app.mainapp'
)

FIXTURE_DIRS = (
   os.path.join(PROJECT_PATH, 'fixtures'),
)

ACCOUNT_ACTIVATION_DAYS = 7
DEFAULT_CHARSET='utf-8'

LANGUAGES = (
  ('fr', 'French'),
  ('en', 'English'),
)

POLITICIAN_NAME = "MP"
POLITICIAN_REPTYPE = "M"
PASSCODE_FILE = os.path.join(PROJECT_PATH, "data/passcodes.csv")

#################################################################################
# These variables Should be defined in the local settings file
#################################################################################
#DATABASE_ENGINE =            # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
#DATABASE_NAME =              # Or path to database file if using sqlite3.
#DATABASE_USER =              # Not used with sqlite3.
#DATABASE_PASSWORD =          # Not used with sqlite3.
#DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
#DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.
#
#EMAIL_USE_TLS =
#EMAIL_HOST =
#EMAIL_HOST_USER =
#EMAIL_HOST_PASSWORD =
#EMAIL_PORT =
#EMAIL_FROM_USER =
#DEBUG =
#Serve media via Django?
#LOCAL_DEV =
#SITE_ROOT=
#SECRET_KEY=
#####################################################################################

# import local settings overriding the defaults
# local_settings.py is machine independent and should not be checked in
try:
    from local_settings import *
except ImportError:
    try:
        from mod_python import apache
        apache.log_error( "local_settings.py not set; using default settings", apache.APLOG_NOTICE )
    except ImportError:
        import sys
        sys.stderr.write( "local_settings.py not set; using default settings\n" )
