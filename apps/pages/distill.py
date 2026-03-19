from __future__ import annotations

from typing import Iterator

from django_distill import distill_path

from apps.core.data_loader import load_cities
from apps.pages import views

SUBSIDY_TYPES = [
    "central_birth_subsidy",
    "birth_bonus",
    "childcare_allowance",
    "daycare_subsidy",
    "parental_leave",
]


def get_all_city_slugs() -> Iterator[dict[str, str]]:
    """Generate city slug parameters for distill."""
    for city in load_cities():
        yield {"slug": city["slug"]}


def get_all_subsidy_types() -> Iterator[dict[str, str]]:
    """Generate subsidy type parameters for distill."""
    for stype in SUBSIDY_TYPES:
        yield {"subsidy_type": stype}


urlpatterns = [
    distill_path("", views.home, name="home"),
    distill_path("subsidies/", views.subsidies_index, name="subsidies_index"),
    distill_path(
        "subsidies/city/<slug:slug>/",
        views.city_detail,
        name="city_detail",
        distill_func=get_all_city_slugs,
    ),
    distill_path(
        "subsidies/type/<str:subsidy_type>/",
        views.type_detail,
        name="type_detail",
        distill_func=get_all_subsidy_types,
    ),
    distill_path(
        "daycare-centers/",
        views.daycare_centers,
        name="daycare_centers",
    ),
    distill_path(
        "daycare-centers/<slug:slug>/",
        views.daycare_centers_city,
        name="daycare_centers_city",
        distill_func=get_all_city_slugs,
    ),
    distill_path("about/", views.about, name="about"),
    distill_path("robots.txt", views.robots_txt, name="robots_txt"),
    distill_path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
]
