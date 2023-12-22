from modules.lru_cache import LRUCache
from modules.multi_hit_lru_cache import MultiHitLRUCache
from modules.paged_lru_cache import PagedLRUCache
from modules.blocks_cache import BlocksCache

__all__ = [
    "LRUCache",
    "PagedLRUCache",
    "MultiHitLRUCache",
    "BlocksCache"
]
