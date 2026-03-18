from .base import *  # noqa: F401, F403

DEBUG = False

ALLOWED_HOSTS = [
    ".github.io",
]

# GitHub Pages deploys under /repo-name/
SITE_PREFIX = "/taiwan-parenting-subsidy"
STATIC_URL = SITE_PREFIX + "/static/"
