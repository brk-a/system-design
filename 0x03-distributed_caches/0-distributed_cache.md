# distributed caches
* what is a cache?
    -  a hardware or software component that stores data so that future requests for that data can be served faster
    - the data stored in a cache might be the result of an earlier computation or a copy of data stored elsewhere
    - a *cache hit* occurs when the requested data can be found in a cache
    - a *cache miss* occurs when the requested data cannot be found in a cache
    - cache hits are served by reading data from the cache which is faster than recomputing a result or reading from a slower data store; the more requests that can be served from the cache, the faster the system performs
* why have a cache
    - make as few network calls as possible
    - avoid repeating computations
    - reduce load on DB
* if caches are that good, why no replace the DB with multiple caches?
    - the HW a cache runs on is more expensive than the one a DB runs on
    - lots of data on a cache increases search time; this defeats the purpose of caching
* when to load and unload data from cache?
    - depends on your cache policy
    - LRU &rarr; Least Recently Used. least recently used entries are evicted first (descending order of time; latest on top)
    - LFU &rarr; Least Frequently Used. counts how often an item is needed; those used less often are discarded first. this is similar to LRU except that how many times a block was accessed is stored instead of how recently. while running an access sequence, the block which was used the fewest times will be removed from the cache
    - find more cache policies [here][def]

    ```mermaid
    flowchart LR
    a((user))--1 request-->b[server]
    b--2 query-->c[(DB)]
    c--3 data-->b
    b-.4 user's profile.->d[cache]
    b--5 response-->a
    ```

[def]: https://en.wikipedia.org/wiki/Cache_replacement_policies