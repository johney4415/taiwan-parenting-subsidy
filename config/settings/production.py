from .base import *  # noqa: F401, F403

DEBUG = False

ALLOWED_HOSTS = [
    ".github.io",
]

# For GitHub Pages static files path
# Change this if using a custom domain (use "/static/")
STATIC_URL = "/static/"
