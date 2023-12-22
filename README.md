# Cache

This is a study of a variety of implementations of cache under specific constraints.

The implementations evaluated are:

1. LRUCache - Implementation of the traditional LRU.
2. PagedLRUCache - A variant of LRU where pages are read and cached.
3. MultiHitLRUCache - Another variant of LRU where we cache the block only if the request was repeated.
4. BlocksCache - An implementation based on LRU where we assume two sizes of blocks: 8K and 64K.


## How to install the dependencies

```
poetry install
```

## How to run the performance evaluation application
```
poetry run python app.py
```

## How to run the tests
```
poetry run pytest
```

## Results of the performance evaluation
| Cache model      | Hits    | Missed  | Hit Ratio |
|------------------|---------|---------|-----------|
| LRUCache         | 140751  | 759177  | 15.64%    |
| PagedLRUCache    | 1123095 | 3474982 | 24.43%    |
| MultiHitLRUCache | 141522  | 758406  | 15.73%    |
| BlocksCache      | 549403  | 350525  | 61.05%    |
