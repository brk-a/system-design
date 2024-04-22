# distributed cache
### the problem
* a web app backed by a data store
* web app could be  an app or service
* data store could be DB or service
* client makes a call to web app which, in turn, makes a call to data store; result is returned to client
* the issues to address are
    1. make as few calls as possible to data store
    2. decrease latency of the system
    3. serve requests as usual, for some period of time, when data store is slow or down
### approach
* build a cache and in memory
* web app talks to the data store IFF there is a cache miss
### why is it called a distributed cache
* data is too large to be stored in one machine/box
* in other words, data is *distributed* among machines
### requirements
#### 1. functional
* implement the following
    * `put(key, value)` &rarr; stores object & sum-unique-key in cache 
    * `get(key)` &rarr; retrieves object by sum-unique-key from cache
#### 2. non-functional
* implement a chache that is
    * scalable &rarr; handles large and small amounts of data proportionally and efficiently
    * available &rarr; data in cache survives hardware and/or network failures
    * fast &rarr; *put*s and *get*s happen quickly
### data structures
* hash table (hash map); has key-value pairs and O(1) retrieval time
    - all well and good until we get to the table's capacity
    - we require an efficient cache eviction policy: LRU
    - hash tables, however, do not store the order in which the data was entered;we need another data structure to compliment the hash table
* a queue that has O(1) time for read, retrieve and delete ops
    - a doubly-linked-list works
    - during `GET`, check whether `key` the cache. if not, return `null`, else, move the k-v pair to the top of the queue and return the `value`

        ```mermaid
        ---
        title: flow of LRU during GET op
        ---
        flowchart TD
            A[GET]-->B{key in cache?}
            B-->|no| C[return null]
            B-->|yes| D[move key-value to head of list and return value]
        ```

    - during `PUT`, check whether `key` is in the cache(use `key` to get value of `value`). id yes, update `value` and move the k-v pair to the top of the queue, else, check if cache is full. if yes, add the new k-v pair to the head of the queue, else, remove the k-v pair that is at the tail of queue and add the new k-v pair to the head of the queue

         ```mermaid
        ---
        title: flow of LRU during PUT op
        ---
        flowchart TD
            A[GET]-->B{key in cache?}
            B-->|no| C{ is cache full?}
            B-->|yes| D[move the k-v pair to the top/head]
            C-->|yes| E[add the new k-v pair to the head]
            C-->|no| F[remove the k-v pair that is at the tail and add the new k-v pair to the head]
        ```

### distributing the cache
* have a cache for each service host
* each host stores a portion of the data
    - example: two service hosts w. a cache each
    - data is indexed alphabetically
    - first cache stores data in the range A to M
    - second cache stores data in the range N to Z
* each host knows about both caches and sends requests to the relevant one

     ```mermaid
    ---
    title: distributed cache (dedicated cache cluster)
    ---
    flowchart TD
    A[service-host-A]-.->B[LRU cache]
    C[service-host-B]-.->D[LRU cache]
    A-.->D
    C-.->B
    ```

    ```mermaid
    ---
    title: distributed cache (co-located cache)
    ---
    flowchart TD
    subgraph service-host-A
    A[server A]-.->B[LRU cache]
    end
    subgraph service-host-B
    C[server B]-.->D[LRU cache]
    end
    A-.->D
    C-.->B
    ```

* dedicated cache cluster vs co-located cache

    |dedicated cache cluster|co-located cache|
    |:---:|:---:|
    |service and cache resources are isolated|no need for extra hardware|
    |can be used by multiple services|cache scales directly proportionally to service|
    |allows flexibility when choosing hardware|less operational cost|

* choosing a cache
    * two approaches: naive and consistent hashing
    * in the naive approach, a service chooses a host using a `mod` function that operates on a hash function, a key and the number of cache hosts. this is not used in production
    <br/>
    $cacheHostNumber = hashFunction(key) \mod numberOfCacheHosts$
    <br/>
    * in the consistent hashing approach, each object is [mapped to a point on a circle][def]; a [unit circle][def2] is best. each cache host will fall on a point on the circle and *"owns"* the space between said host and the nearest anti-clockwise neighbour (or clockwise, depending on your configuration). the position of each host will not change no matter how many more hosts are added; if a host is mapped between two existing ones, it assumes the range of keys to its left (anti-clockwise) or right (clockwise) depending on configuration

[def]: https://math.libretexts.org/Courses/North_Hennepin_Community_College/Math_1120%3A_College_Algebra_(Lang)/06%3A_Trigonometric_Functions_of_Angles/6.03%3A_Points_on_Circles_Using_Sine_and_Cosine
[def2]: https://math.libretexts.org/Courses/City_University_of_New_York/College_Algebra_and_Trigonometry-_Expressions_Equations_and_Graphs/04%3A_Introduction_to_Trigonometry_and_Transcendental_Expressions/4.01%3A_Trigonometric_Expressions/4.1.04%3A_The_Unit_Circle