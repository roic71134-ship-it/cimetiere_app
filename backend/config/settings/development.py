from .base import *

DEBUG = True

# CORS élargi en développement
CORS_ALLOW_ALL_ORIGINS = True

# Logs
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "apps": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}