from flask_minify.utils import get_optimized_hashing


class MemoryCache:
    def __init__(self, store_key_getter=None, limit=0):
        self.store_key_getter = store_key_getter
        self.limit = limit
        self._cache = {}
        self.hashing = get_optimized_hashing()

    @property
    def store(self):
        if self.store_key_getter:
            return self._cache.setdefault(self.store_key_getter(), {})

        return self._cache

    @property
    def limit_exceeded(self):
        return len(self.store) >= self.limit

    def __getitem__(self, key):
        return self.store.get(key)

    def __setitem__(self, key, value):
        if self.limit_exceeded:
            self.store.popitem()

        self.store.update({key: value})

    def get_or_set(self, key, getter):
        if self.limit == 0:
            return getter()

        hashed_key = self.hashing(key.encode("utf-8")).hexdigest()

        if not self[hashed_key]:
            self[hashed_key] = getter()

        return self[hashed_key]

    def clear(self):
        del self._cache
        self._cache = {}
