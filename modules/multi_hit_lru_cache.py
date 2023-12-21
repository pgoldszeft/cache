from collections import OrderedDict
from typing import Any

from modules import LRUCache


class MultiHitLRUCache(LRUCache):
    def __init__(self, max_uncached_requests: int, cache_after: int = 1, *args: Any, **kwargs: Any) -> None:
        self.uncached_requests = OrderedDict()
        self.max_uncached_requests = max_uncached_requests
        self.cache_after = cache_after
        super().__init__(*args, **kwargs)

    def __call__(self, offset: int, size: int) -> bytes:
        key = (offset, size)
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]

        data = self.read_function(offset, size)

        self.uncached_requests[key] = self.uncached_requests.get(key, 0) + 1
        if self.uncached_requests[key] <= self.cache_after:
            self.uncached_requests.move_to_end(key)
            if len(self.uncached_requests) > self.max_uncached_requests:
                self.uncached_requests.popitem(last=False)
        else:
            self.uncached_requests.pop(key, None)
            self.cache[key] = data
            self.used_size += size
            while self.used_size > self.cache_size:
                evicted_key, _ = self.cache.popitem(last=False)
                self.used_size -= evicted_key[1]
        return data
