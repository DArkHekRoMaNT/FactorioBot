def first(iterable, *, matcher=None, default=None):
    if matcher:
        for item in iterable:
            if matcher(item):
                return item
    else:
        for item in iterable:
            return item

    return default
