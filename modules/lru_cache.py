from collections import OrderedDict
from typing import Callable


class LRUCache:
    def __init__(self, read_function: Callable[[int, int], bytes], cache_size: int) -> None:
        self.cache = OrderedDict()
        self.cache_size = cache_size
        self.read_function = read_function
        self.used_size = 0
        self.hits = 0
        self.missed = 0

    def __call__(self, offset: int, size: int) -> bytes:
        key = (offset, size)
        if key in self.cache:
            self.cache.move_to_end(key)
            self.hits += 1
            return self.cache[key]

        data = self.read_function(offset, size)
        self.cache[key] = data
        self.used_size += size
        self.missed += 1

        while self.used_size > self.cache_size:
            evicted_key, _ = self.cache.popitem(last=False)
            self.used_size -= evicted_key[1]

        return data

    def keys(self) -> list[tuple[int, int]]:
        return list(self.cache.keys())

    def values(self) -> list[bytes]:
        return list(self.cache.values())

    def __contains__(self, key: tuple) -> bool:
        return key in self.cache

    def __len__(self) -> int:
        return len(self.cache)
