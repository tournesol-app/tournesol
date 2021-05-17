from time import time


class CacheTimeoutMaxMem(object):
    """Cache objects with a timeout, with a maximal number of objects."""
    def __init__(self, timeout_s=10, max_entries=10):
        self.timeout_s = timeout_s
        self.max_entries = max_entries

        # format: key -> dict {value -> value, created -> timestamp}
        self.entries = {}

    def clean(self):
        """Remove old objects."""
        n_objects = len(self.entries)
        if n_objects <= self.max_entries:
            return

        oldest_to_newest = sorted(list(self.entries.keys()),
                                  key=lambda x: self.entries[x]['created'])
        for key in oldest_to_newest[:n_objects - self.max_entries]:
            del self.entries[key]

    def set(self, key, value):
        """Remember an key-value pair."""
        self.entries[key] = {'value': value, 'created': time()}
        self.clean()

    def get(self, key):
        """Get an element by key."""
        if key in self.entries:
            # invalidating old entry
            if time() - self.entries[key]['created'] > self.timeout_s:
                del self.entries[key]
                raise KeyError(key)

            # entry is recent enough
            return self.entries[key]['value']
        else:
            raise KeyError(key)


def cache_timeout_maxmem(timeout_s, max_entries):
    """Cache results of a function call."""
    cache = CacheTimeoutMaxMem(timeout_s=timeout_s, max_entries=max_entries)

    def decorator(f, cache=cache):
        def inner(*args, cache=cache, **kwargs):
            key = str(args) + '_'.join([f'{key}:{value}' for key, value in kwargs.items()])
            try:
                result = cache.get(key)
                return result
            except KeyError:
                result = f(*args, **kwargs)
                cache.set(key, result)
                return result
        return inner

    return decorator
