"""
Implementation for a LRU Cache Decorator

This helps reduce API calls by caching the results of a function
"""

import pickle
import os
from collections import OrderedDict

CACHE_PATH = "cache/cache.pkl"
CACHE_LIMIT = 100

def load_cache() -> OrderedDict:
    try:
        with open(CACHE_PATH, "rb") as f:
            return pickle.load(f)
    except:
        return OrderedDict()  # Return an empty ordered dictionary if no cache file exists
    
def save_cache(cache: OrderedDict) -> None:
    folder = os.path.dirname(CACHE_PATH)
    if not os.path.exists(folder):
        os.makedirs(folder)

    with open(CACHE_PATH, "wb") as f:
        pickle.dump(cache, f)

def clear_cache() -> None:
    if os.path.exists(CACHE_PATH):
        os.remove(CACHE_PATH)

def lru_cache(func):
    cache = load_cache()  # Load existing cache

    def make_hashable(item):
        if isinstance(item, list):
            return tuple(item)
        elif isinstance(item, dict):
            return frozenset((k, make_hashable(v)) for k, v in item.items())
        return item

    def wrapper(*args, **kwargs):
        hashable_args = tuple(make_hashable(arg) for arg in args)
        hashable_kwargs = frozenset((k, make_hashable(v)) for k, v in kwargs.items())

        key = (hashable_args, hashable_kwargs)

        if key in cache:
            cache.move_to_end(key)  # Mark as recently used
            return cache[key]

        result = func(*args, **kwargs)
        cache[key] = result
        cache.move_to_end(key)

        if len(cache) > CACHE_LIMIT:
            cache.popitem(last=False)  # Remove least recently used item

        save_cache(cache)
        return result

    return wrapper
