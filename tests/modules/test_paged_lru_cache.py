from modules.paged_lru_cache import PagedLRUCache
from tests.modules.utils import fake_read


class TestPagedLRUCache:
    def test_requests_of_same_block(self):
        cache = PagedLRUCache(read_function=fake_read, cache_size=1000, block_size=500)

        cache(offset=0, size=100)
        cache(offset=10, size=200)

        assert cache.keys() == [(0, 500)]

        assert cache.values() == [
            b'{"offset": 0, "size": 500}',
        ]

        assert len(cache) == 1
        assert cache.used_size == 500

    def test_cross_block_request(self):
        cache = PagedLRUCache(read_function=fake_read, cache_size=1000, block_size=500)

        cache(offset=100, size=500)

        assert len(cache) == 2
        assert cache.used_size == 1000

    def test_repeated_cross_block_request(self):
        num_requests = 0

        def mock_read(offset: int, size: int) -> bytes:
            nonlocal num_requests
            num_requests += 1
            return fake_read(offset, size)

        cache = PagedLRUCache(read_function=mock_read, cache_size=1000, block_size=500)

        for i in range(500):
            cache(offset=i, size=500)

        assert len(cache) == 2
        assert cache.used_size == 1000
        assert num_requests == 2

    def test_request_size_larger_than_cache(self):
        requests = []

        def mock_read(offset: int, size: int) -> bytes:
            nonlocal requests
            requests.append((offset, size))
            return fake_read(offset, size)

        cache = PagedLRUCache(read_function=mock_read, cache_size=1000, block_size=500)

        cache(offset=100, size=1500)

        assert len(cache) == 2
        assert cache.used_size == 1000
        assert len(requests) == 4
        assert requests == [(0, 500), (500, 500), (1000, 500), (1500, 500)]
