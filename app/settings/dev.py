from django.core.handlers.wsgi import WSGIRequest

from .base import *  # noqa: F403

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += [
    'strawberry_django_plus.middlewares.debug_toolbar.DebugToolbarMiddleware',
]

# Debug Toolbar

DEBUG_TOOLBAR = os.getenv('DEBUG_TOOLBAR', False) == 'true'


def show_debug_toolbar(request: WSGIRequest) -> bool:
    return DEBUG_TOOLBAR


DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': show_debug_toolbar,
}

# used for graphiql debug toolbar
INTERNAL_IPS = []
if DEBUG and DEBUG_TOOLBAR:
    INTERNAL_IPS = type(str('c'), (), {'__contains__': lambda *a: True})()

# GraphQL

GRAPHQL_JWT.update({'JWT_COOKIE_SECURE': False})
