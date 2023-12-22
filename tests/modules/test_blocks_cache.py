import pytest

from modules import BlocksCache
from tests.modules.utils import fake_read


class TestBlocksCache:
    @pytest.mark.parametrize(
        "block_size", [BlocksCache.SMALL_BLOCK_SIZE, BlocksCache.LARGE_BLOCK_SIZE]
    )
    def test_request_block(self, block_size):
        cache = BlocksCache(
            read_function=fake_read, cache_size=block_size * 10
        )
        cache(offset=100, size=block_size)
        assert cache.used_size == block_size

    @pytest.mark.parametrize(
        "block_size", [BlocksCache.SMALL_BLOCK_SIZE, BlocksCache.LARGE_BLOCK_SIZE]
    )
    def test_request_many_small_blocks(self, block_size):
        cache = BlocksCache(
            read_function=fake_read, cache_size=block_size * 10
        )

        cache(offset=100, size=block_size)

        assert cache.used_size == block_size

    @pytest.mark.parametrize(
        "block_size", [BlocksCache.SMALL_BLOCK_SIZE, BlocksCache.LARGE_BLOCK_SIZE]
    )
    def test_request_many_small_different_blocks(self, block_size):
        cache = BlocksCache(
            read_function=fake_read, cache_size=block_size * 10
        )

        for i in range(10):
            cache(offset=i, size=block_size)

        assert cache.used_size == 10 * block_size

    @pytest.mark.parametrize(
        "block_size", [BlocksCache.SMALL_BLOCK_SIZE, BlocksCache.LARGE_BLOCK_SIZE]
    )
    def test_request_more_blocks_than_the_cache_capacity(self, block_size):
        cache = BlocksCache(
            read_function=fake_read, cache_size=block_size * 10
        )

        for i in range(100):
            cache(offset=i, size=block_size)

        assert cache.used_size == 10 * block_size

    def test_mixed_requests(self):
        cache_size = BlocksCache.LARGE_BLOCK_SIZE * 3
        cache = BlocksCache(
            read_function=fake_read, cache_size=cache_size
        )

        cache(offset=100, size=BlocksCache.LARGE_BLOCK_SIZE)
        cache(offset=200, size=BlocksCache.SMALL_BLOCK_SIZE)

        assert cache.used_size == BlocksCache.LARGE_BLOCK_SIZE + BlocksCache.SMALL_BLOCK_SIZE

    def test_small_block_and_large_block_with_same_offset(self):
        cache_size = BlocksCache.LARGE_BLOCK_SIZE * 3
        cache = BlocksCache(
            read_function=fake_read, cache_size=cache_size
        )

        cache(offset=100, size=BlocksCache.LARGE_BLOCK_SIZE)
        cache(offset=100, size=BlocksCache.SMALL_BLOCK_SIZE)

        assert cache.used_size == BlocksCache.LARGE_BLOCK_SIZE
        assert len(cache.small_blocks) == 0
        assert len(cache.large_blocks) == 1

    def test_eviction_when_only_large_blocks(self):
        cache_size = BlocksCache.LARGE_BLOCK_SIZE * 3
        cache = BlocksCache(
            read_function=fake_read, cache_size=cache_size
        )

        cache(offset=100, size=BlocksCache.LARGE_BLOCK_SIZE)
        cache(offset=200, size=BlocksCache.LARGE_BLOCK_SIZE)
        cache(offset=300, size=BlocksCache.LARGE_BLOCK_SIZE)
        cache(offset=400, size=BlocksCache.LARGE_BLOCK_SIZE)

        assert cache.used_size == BlocksCache.LARGE_BLOCK_SIZE * 3
        assert len(cache.small_blocks) == 0
        assert len(cache.large_blocks) == 3
        assert next(iter(cache.large_blocks)) == 200

    def test_eviction_when_only_short_blocks(self):
        cache_size = BlocksCache.SMALL_BLOCK_SIZE * 3
        cache = BlocksCache(
            read_function=fake_read, cache_size=cache_size
        )

        cache(offset=100, size=BlocksCache.SMALL_BLOCK_SIZE)
        cache(offset=200, size=BlocksCache.SMALL_BLOCK_SIZE)
        cache(offset=300, size=BlocksCache.SMALL_BLOCK_SIZE)
        cache(offset=400, size=BlocksCache.SMALL_BLOCK_SIZE)

        assert cache.used_size == BlocksCache.SMALL_BLOCK_SIZE * 3
        assert len(cache.small_blocks) == 3
        assert len(cache.large_blocks) == 0
        assert next(iter(cache.small_blocks)) == 200

    def test_eviction_with_mixed_blocks(self):
        cache_size = BlocksCache.SMALL_BLOCK_SIZE * 3
        cache = BlocksCache(
            read_function=fake_read, cache_size=cache_size
        )

        cache(offset=100, size=BlocksCache.SMALL_BLOCK_SIZE)
        cache(offset=200, size=BlocksCache.LARGE_BLOCK_SIZE)
        cache(offset=300, size=BlocksCache.SMALL_BLOCK_SIZE)
        cache(offset=400, size=BlocksCache.LARGE_BLOCK_SIZE)

        assert cache.used_size == (
            BlocksCache.SMALL_BLOCK_SIZE * 1 + BlocksCache.LARGE_BLOCK_SIZE * 1
        )
        assert len(cache.small_blocks) == 1
        assert len(cache.large_blocks) == 1
