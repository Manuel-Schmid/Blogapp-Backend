try:
    from .base import *  # noqa: F403, F401
except ImportError:
    pass

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}

TEST = True
