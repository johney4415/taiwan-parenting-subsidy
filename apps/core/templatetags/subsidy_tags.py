from __future__ import annotations

from django import template

register = template.Library()


@register.filter
def currency(value: int | float) -> str:
    """Format a number as currency with comma separators."""
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return str(value)
