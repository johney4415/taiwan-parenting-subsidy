from django.urls import path

from . import views

app_name = "pages"

urlpatterns = [
    path("", views.home, name="home"),
    path("subsidies/", views.subsidies_index, name="subsidies_index"),
    path("subsidies/city/<slug:slug>/", views.city_detail, name="city_detail"),
    path("subsidies/type/<str:subsidy_type>/", views.type_detail, name="type_detail"),
    path("daycare-centers/", views.daycare_centers, name="daycare_centers"),
    path(
        "daycare-centers/<slug:slug>/",
        views.daycare_centers_city,
        name="daycare_centers_city",
    ),
    path("about/", views.about, name="about"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
]
