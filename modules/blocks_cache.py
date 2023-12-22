from collections import OrderedDict
from datetime import datetime
from dataclasses import dataclass
from typing import Callable, Any


@dataclass
class BlockDescriptor:
    offset: int
    size: int
    cached_at: datetime
    data: bytes


class BlocksOrderedDict(OrderedDict):
    def __init__(self, block_size: int, *args: Any, **kwargs: Any) -> None:
        self.block_size = block_size
        super().__init__(*args, **kwargs)

    def __setitem__(self, offset: int, data: bytes) -> None:
        block = BlockDescriptor(
            offset=offset, size=self.block_size, data=data, cached_at=datetime.now()
        )
        super().__setitem__(offset, block)
        self.move_to_end(offset)

    def __getitem__(self, offset: int) -> bytes:
        block = super().__getitem__(offset)
        block.cached_at = datetime.now()
        self.move_to_end(offset)
        return block.data

    def next_cached_at(self) -> datetime:
        if len(self) == 0:
            return datetime.fromtimestamp(0)

        block = next(iter(self.values()))
        return block.cached_at

    @property
    def total_size(self) -> int:
        return len(self) * self.block_size


class BlocksCache:
    SMALL_BLOCK = 1
    LARGE_BLOCK = 2

    SMALL_BLOCK_SIZE = 8 * 1024
    LARGE_BLOCK_SIZE = 16 * 1024

    def __init__(self, read_function: Callable[[int, int], bytes], cache_size: int):
        self.small_blocks = BlocksOrderedDict(self.SMALL_BLOCK_SIZE)
        self.large_blocks = BlocksOrderedDict(self.LARGE_BLOCK_SIZE)
        self.read_function = read_function
        self.cache_size = cache_size
        self.hits = 0
        self.missed = 0

    def __call__(self, offset: int, size: int) -> bytes:
        result = (
            self._handle_small_block(offset, size)
            if size == self.SMALL_BLOCK_SIZE
            else self._handle_large_block(offset, size)
        )
        self._evict_blocks()

        return result

    def _handle_small_block(self, offset: int, size: int) -> bytes:
        if offset in self.small_blocks:
            self.hits += 1
            return self.small_blocks[offset]

        if offset in self.large_blocks:
            data = self.large_blocks[offset][:self.SMALL_BLOCK_SIZE]
            self.large_blocks[offset] = data
            self.hits += 1
            return data

        data = self.read_function(offset, size)
        self.small_blocks[offset] = data
        self.missed += 1
        return data

    def _handle_large_block(self, offset: int, size: int) -> bytes:
        if offset in self.large_blocks:
            self.hits += 1
            return self.large_blocks[offset]

        data = self.read_function(offset, size)
        self.large_blocks[offset] = data
        self.missed += 1
        return data

    @property
    def used_size(self) -> int:
        return self.large_blocks.total_size + self.small_blocks.total_size

    def _evict_blocks(self):
        while self.used_size > self.cache_size:
            if self.small_blocks.total_size == 0 and self.large_blocks.total_size > 0:
                cache = self.large_blocks
            elif self.small_blocks.total_size > 0 and self.large_blocks.total_size == 0:
                cache = self.small_blocks
            else:
                if self.small_blocks.next_cached_at() < self.large_blocks.next_cached_at():
                    cache = self.small_blocks
                else:
                    cache = self.large_blocks

            cache.popitem(last=False)
