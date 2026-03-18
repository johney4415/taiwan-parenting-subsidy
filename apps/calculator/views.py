from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.core.data_loader import load_cities


def calculator(request: HttpRequest) -> HttpResponse:
    """Interactive subsidy calculator page."""
    return render(
        request,
        "pages/calculator.html",
        {
            "cities": load_cities(),
        },
    )
