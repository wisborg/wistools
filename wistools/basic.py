"""
Various basic utilities such as working with iterables
"""


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
