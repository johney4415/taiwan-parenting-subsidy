from __future__ import annotations

from django.conf import settings
from django.http import HttpRequest


def site_prefix(request: HttpRequest) -> dict[str, str]:
    """Add SITE_PREFIX to template context for building absolute URLs."""
    return {"SITE_PREFIX": getattr(settings, "SITE_PREFIX", "")}
