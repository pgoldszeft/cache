from modules import MultiHitLRUCache
from tests.modules.utils import fake_read


class TestMultiHitLRUCache:
    def test_single_request_is_not_stored(self):
        cache = MultiHitLRUCache(
            read_function=fake_read,
            cache_size=1000,
            max_uncached_requests=int(1000/500)
        )

        cache(offset=0, size=100)
        cache(offset=10, size=200)

        assert len(cache) == 0
        assert cache.used_size == 0

    def test_multi_requests_are_stored(self):
        cache = MultiHitLRUCache(
            read_function=fake_read,
            cache_size=1000,
            max_uncached_requests=int(1000/500)
        )

        cache(offset=0, size=100)
        cache(offset=10, size=200)
        cache(offset=0, size=100)

        assert len(cache) == 1
        assert cache.used_size == 100

        assert (0, 100) in cache
        assert (10, 200) not in cache

    def test_cached_request_not_evicted_with_new_request(self):
        cache = MultiHitLRUCache(
            read_function=fake_read,
            cache_size=100,
            max_uncached_requests=int(1000/500)
        )

        cache(offset=0, size=100)
        cache(offset=0, size=100)
        cache(offset=10, size=100)

        assert len(cache) == 1
        assert cache.used_size == 100

        assert (0, 100) in cache
        assert (10, 100) not in cache

    def test_cached_request_replaced_with_new_repeated_request(self):
        cache = MultiHitLRUCache(
            read_function=fake_read,
            cache_size=100,
            max_uncached_requests=int(1000/500)
        )

        cache(offset=0, size=100)
        cache(offset=0, size=100)
        cache(offset=10, size=100)
        cache(offset=10, size=100)

        assert len(cache) == 1
        assert cache.used_size == 100

        assert (0, 100) not in cache
        assert (10, 100) in cache
