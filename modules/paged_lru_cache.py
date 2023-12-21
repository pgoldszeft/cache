from math import trunc, ceil
from typing import Any

from modules import MultiHitLRUCache


DEFAULT_BLOCK_SIZE = 8 * 1024


class PagedLRUCache(MultiHitLRUCache):
    def __init__(self, cache_size: int, block_size: int = DEFAULT_BLOCK_SIZE, *args: Any, **kwargs: Any):
        self.block_size = block_size
        max_uncached_requests = int(cache_size / block_size)
        super().__init__(
            cache_size=cache_size,
            max_uncached_requests = max_uncached_requests,
            *args, **kwargs
        )

    def __call__(self, offset: int, size: int) -> bytes:
        first_block_id = trunc(offset/self.block_size)
        first_block_offset = first_block_id * self.block_size

        last_block_id = ceil((offset+size)/self.block_size)
        last_block_offset = last_block_id * self.block_size

        result = b""
        for block_offset in range(first_block_offset, last_block_offset, self.block_size):
            result += super().__call__(block_offset, self.block_size)
        return result
