import pickle

CACHE_PATH = "cache/cache.pkl"
# Cache decorator to reduce API calls
def cache(func):

    def wrapper(*args, **kwargs):
        try:
            with open(CACHE_PATH, "rb") as f:
                cache = pickle.load(f)
        except:
            cache = {}

        key = (args, frozenset(kwargs.items()))
        
        if key in cache:
            return cache[key]
        
        result = func(*args, **kwargs)
        cache[key] = result
        
        with open(CACHE_PATH, "wb") as f:
            pickle.dump(cache, f)
            
        return result
    
    return wrapper