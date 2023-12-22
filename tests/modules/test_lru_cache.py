from modules.lru_cache import LRUCache
from tests.modules.utils import fake_read


class TestCache:
    def test_cache_populated_properly(self):
        cache = LRUCache(read_function=fake_read, cache_size=1000)

        cache(offset=0, size=100)
        cache(offset=10, size=200)

        assert cache.keys() == [
            (0, 100), (10, 200)
        ]

        assert cache.values() == [
            b'{"offset": 0, "size": 100}',
            b'{"offset": 10, "size": 200}'
        ]

        assert len(cache) == 2
        assert cache.used_size == 300

    def test_block_eviction(self):
        cache = LRUCache(read_function=fake_read, cache_size=100)

        cache(offset=0, size=50)
        cache(offset=1, size=50)
        cache(offset=2, size=50)

        assert (0, 50) not in cache
        assert len(cache) == 2
        assert cache.used_size == 100

    def test_block_repetition(self):
        cache = LRUCache(read_function=fake_read, cache_size=100)

        cache(offset=0, size=50)
        cache(offset=0, size=50)
        cache(offset=0, size=50)

        assert len(cache) == 1
        assert cache.keys() == [(0, 50)]

    def test_blocks_with_different_offsets(self):
        cache = LRUCache(read_function=fake_read, cache_size=100)

        for i in range(10):
            cache(offset=i, size=10)

        assert len(cache) == 10
        assert cache.used_size == 100

    def test_misses(self):
        cache = LRUCache(read_function=fake_read, cache_size=100)

        for i in range(10):
            cache(offset=i, size=10)

        assert cache.hits == 0
        assert cache.missed == 10

    def test_hits(self):
        cache = LRUCache(read_function=fake_read, cache_size=100)

        for _ in range(10):
            cache(offset=0, size=10)

        assert cache.hits == 9
        assert cache.missed == 1
