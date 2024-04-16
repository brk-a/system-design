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

* cache thrashing
    - cache thrash is caused by an ongoing computer activity that fails to progress due to excessive use of resources or conflicts in the caching system
    -  the computer will, typically, take the same actions over and over in an attempt to complete the desired task. one process diverts resources from another process which, in turn, must take resources from another process; a vicious cycle if the total resources available are insufficient
* where should the cache be placed?
    - eea...sy! either close t the server(s) or close to the DB
    - say we place it close to the server(s)
        * placing the cache in-memory means zero network calls on one hand and limited capacity on the other. there is, also, the single-point-of-failure-problem on the servers created by this configuration. data consistency may be a problem too
    - say we place it between the server(s) and DB, that is, have a distributed global cache
        * all servers will hit the same cache; the call is forwarded to the DB IFF there is a miss (example, [Redis][def2])
        * slower but more accurate than the first option
        * little to no downtime on the system if a server crashes
        * single-point-of-failure-problem moves from servers to cache, however, cache can be scaled and distributed to neutralise the problem
        * there is data consistency w/i the cache system

        ```mermaid
        ---
        title: cache between servers and DB
        ---
        flowchart LR
        A[server 1]<-->B[cache]
        C[server 2]<-->B
        D[server N]<-->B
        B<-->E[(DB)]
        ```

* what will be the cache write policy?
    - one of the following: write-through and write-back
    - write-through: data is written in the cache before being written in the DB
    - example: user changes password. new hashed password is saved to cache. cache updates DB
    - write-back: data is written in the DB before being written on the cache
    - example: user changes password. new hashed password is written to DB. DB updates cache when cache makes the query
    - how will data consistency be achieved in a distributed cache config?
        * to begin with, stay away from the typical write-through policy
        * also, do not implement the typical write-back policy
        * write the changes to one box on the cache system. serve all requests from that box. let a reasonable time pass, say, 10s. perform a batch write to the DB. check if DB and cache are in sync: if not, sync
        * in other words, take a hybrid-*ish* approach
        * this method is best for non-critical data
        * perform a write-back-first hybrid operation when dealing with critical/sensitive data

[def]: https://en.wikipedia.org/wiki/Cache_replacement_policies
[def2]: https://redis.io/