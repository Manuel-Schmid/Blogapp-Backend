try:
    from .base import *  # noqa: F403, F401
except ImportError:
    pass

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}

MEDIA_ROOT = os.path.join(BASE_DIR, 'blog/tests/media/uploaded_test_files')

TEST = True
