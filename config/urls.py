from django.conf import settings
from django.urls import include, path

urlpatterns = [
    path("", include("apps.pages.urls")),
    path("calculator/", include("apps.calculator.urls")),
]

# django-distill: register distill URLs for static generation
if "django_distill" in settings.INSTALLED_APPS:
    from apps.calculator.distill import urlpatterns as calc_distill_urls
    from apps.pages.distill import urlpatterns as pages_distill_urls

    urlpatterns = pages_distill_urls + calc_distill_urls
