from django_distill import distill_path

from . import views

urlpatterns = [
    distill_path("calculator/", views.calculator, name="calculator"),
]
