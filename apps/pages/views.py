from __future__ import annotations

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render

from apps.core.data_loader import (
    get_city_by_slug,
    get_city_subsidies,
    load_all_subsidies,
    load_birth_bonus,
    load_cities,
)

SUBSIDY_TYPE_LABELS: dict[str, str] = {
    "central_birth_subsidy": "中央生育補助（保底10萬）",
    "birth_bonus": "各縣市生育獎勵金",
    "childcare_allowance": "育兒津貼",
    "daycare_subsidy": "托育補助",
    "parental_leave": "育嬰留停津貼",
}


def home(request: HttpRequest) -> HttpResponse:
    """Home page with quick navigation."""
    cities = load_cities()
    regions: dict[str, list[dict]] = {}
    for city in cities:
        region = city["region"]
        regions.setdefault(region, []).append(city)

    return render(
        request,
        "pages/home.html",
        {
            "cities": cities,
            "regions": regions,
            "subsidy_types": SUBSIDY_TYPE_LABELS,
        },
    )


def subsidies_index(request: HttpRequest) -> HttpResponse:
    """Overview of all subsidy types."""
    return render(
        request,
        "pages/subsidies/index.html",
        {
            "subsidy_types": SUBSIDY_TYPE_LABELS,
            "cities": load_cities(),
            "birth_bonus": load_birth_bonus(),
        },
    )


def city_detail(request: HttpRequest, slug: str) -> HttpResponse:
    """Detail page for a specific city's subsidies."""
    city = get_city_by_slug(slug)
    if city is None:
        raise Http404(f"City not found: {slug}")

    subsidies = get_city_subsidies(city["code"])

    return render(
        request,
        "pages/subsidies/city_detail.html",
        {
            "city": city,
            "subsidies": subsidies,
        },
    )


def type_detail(request: HttpRequest, subsidy_type: str) -> HttpResponse:
    """Cross-city comparison for a specific subsidy type."""
    if subsidy_type not in SUBSIDY_TYPE_LABELS:
        raise Http404(f"Unknown subsidy type: {subsidy_type}")

    all_subsidies = load_all_subsidies()
    cities = load_cities()

    return render(
        request,
        "pages/subsidies/type_detail.html",
        {
            "subsidy_type": subsidy_type,
            "subsidy_label": SUBSIDY_TYPE_LABELS[subsidy_type],
            "data": all_subsidies.get(subsidy_type, {}),
            "cities": cities,
        },
    )


def about(request: HttpRequest) -> HttpResponse:
    """About page with disclaimers."""
    return render(request, "pages/about.html")


def robots_txt(request: HttpRequest) -> HttpResponse:
    """Generate robots.txt."""
    content = "User-agent: *\nAllow: /\nSitemap: /sitemap.xml\n"
    return HttpResponse(content, content_type="text/plain")


def sitemap_xml(request: HttpRequest) -> HttpResponse:
    """Generate sitemap.xml with all pages."""
    cities = load_cities()
    subsidy_types = SUBSIDY_TYPE_LABELS.keys()

    urls = [
        "/",
        "/subsidies/",
        "/calculator/",
        "/about/",
    ]
    for city in cities:
        urls.append(f"/subsidies/city/{city['slug']}/")
    for stype in subsidy_types:
        urls.append(f"/subsidies/type/{stype}/")

    xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for url in urls:
        xml_lines.append(f"  <url><loc>{url}</loc></url>")
    xml_lines.append("</urlset>")

    return HttpResponse("\n".join(xml_lines), content_type="application/xml")
