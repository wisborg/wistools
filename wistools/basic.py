"""
Various basic utilities such as working with iterables
"""

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo


def iterate(items):
    """Allow iterating over anything. Strings and bytes are considered
    scalars for this purpose to avoid iterating over the indvidual
    characters/bytes."""
    if isinstance(items, (str, bytes)):
        # Avoid iterating over individual characters/bytes
        items = [items]
    try:
        iter(items)
        yield from items
    except TypeError:
        yield items


def round_decimal(value: Decimal, fmt: str) -> Decimal:
    """Round decimal values using the ROUND_HALF_UP rule."""
    return value.quantize(Decimal(fmt), rounding=ROUND_HALF_UP)


def as_timezone(value: datetime, tz_name: str) -> datetime:
    return value.astimezone(ZoneInfo(tz_name))
