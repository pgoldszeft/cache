import random
from enum import Enum

from modules import LRUCache, PagedLRUCache, MultiHitLRUCache, BlocksCache

SMALL_SIZE = 8 * 1024
LARGE_SIZE = 64 * 1024
NUM_REQUESTS = 1000000
CACHE_SIZE = 10 * 1024 * 1024
FILE_SIZE = 200 * 1024 * 1024


class RequestType(Enum):
    SMALL = 0,
    LARGE = 1,
    SMALL_PLUS_LARGE = 2


def create_requests() -> list[tuple[int, int]]:
    random.seed(123)

    weights = {
        RequestType.SMALL.value: 0.5,
        RequestType.LARGE.value: 0.4,
        RequestType.SMALL_PLUS_LARGE: 0.1
    }

    request_types = random.choices(
        population=list(weights.keys()),
        weights=list(weights.values()),
        k=NUM_REQUESTS
    )

    requests = []
    small_plus_large_index = 0
    small_plus_large_offset = 0

    offsets = random.choices(
        population=random.choices(range(0, FILE_SIZE-LARGE_SIZE-1), k=1000),
        k=NUM_REQUESTS
    )

    for i in range(NUM_REQUESTS):

        type = request_types[i]

        if i == small_plus_large_index:
            offset = small_plus_large_offset
            small_plus_large_index = 0
            requests.append(
                (offset, LARGE_SIZE)
            )

        match type:
            case RequestType.SMALL.value:
                requests.append(
                    (offsets[i], SMALL_SIZE)
                )
            case RequestType.LARGE.value:
                requests.append(
                    (offsets[i], LARGE_SIZE)
                )
            case RequestType.SMALL_PLUS_LARGE.value:
                small_plus_large_offset = offsets[i]
                small_plus_large_index = i + random.randint(10, 100)
                requests.append(
                    (small_plus_large_offset, SMALL_SIZE)
                )

        if len(requests) >= NUM_REQUESTS:
            break

    return requests


def simulate_requests(
    requests: list[tuple[int, int]],
    cache: LRUCache | PagedLRUCache | MultiHitLRUCache | BlocksCache
) -> None:
    for request in requests:
        cache(*request)
    print(
        f"{type(cache).__name__}: "
        f"hits: {cache.hits}, "
        f"missed: {cache.missed}, "
        f"hit ratio: {cache.hits/(cache.hits+cache.missed)*100}"
    )


if __name__ == "__main__":
    def fake_read_function(offset: int, size: int) -> bytes:
        return b"fake_data"

    requests = create_requests()

    lru_cache = LRUCache(read_function=fake_read_function, cache_size=CACHE_SIZE)
    simulate_requests(requests, lru_cache)

    paged_lru_cache = PagedLRUCache(
        read_function=fake_read_function,
        cache_size=CACHE_SIZE,
        block_size=SMALL_SIZE,
    )
    simulate_requests(requests, paged_lru_cache)

    multi_hit_lru_cache = MultiHitLRUCache(
        read_function=fake_read_function,
        cache_size=CACHE_SIZE,
        max_uncached_requests=int(CACHE_SIZE/SMALL_SIZE)
    )
    simulate_requests(requests, multi_hit_lru_cache)

    blocks_cache = BlocksCache(read_function=fake_read_function, cache_size=CACHE_SIZE)
    simulate_requests(requests, blocks_cache)
