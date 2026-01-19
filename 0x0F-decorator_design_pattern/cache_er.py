#!/usr/bin/env python

class CacheDecorator:
        def __init__(self, wrapped):
            self._wrapped = wrapped
            self.cache = {}

        def __call__(self, *args, **kwargs):
            if args in self.cache:
                print("Returning cached result")
                return self.cache[args]
            result = self._wrapped(*args, **kwargs)
            self.cache[args] = result
            return result

def get_user_from_db(user_id):
    print("Fetching from DB...")
    return f'User {user_id} details'

if __name__ == '__main__':
    cached_user = CacheDecorator(get_user_from_db)
    print(cached_user(1))  # Fetch from DB
    print(cached_user(1))  # Return from cache