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
* build a cache ~~and in memory~~
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
* implement a cache that is
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
            A[PUT]-->B{key in cache?}
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
    * method [sharding][def3]
    * two approaches: naive and consistent hashing
    * in the naive approach, a service chooses a host using a `mod` function that operates on a hash function, a key and the number of cache hosts. this is not used in production<br/>
    $cacheHostNumber = hashFunction(key) \mod numberOfCacheHosts$
    * <br/> in the consistent hashing approach, each object is [mapped to a point on a circle][def]; a [unit circle][def2] is best. each cache host will fall on a point on the circle and *"owns"* the space between said host and the nearest anti-clockwise neighbour (or clockwise, depending on your configuration). the position of each host will not change no matter how many more hosts are added; if a host is mapped between two existing ones, it assumes the range of keys to its left (anti-clockwise) or right (clockwise) depending on configuration
    * cache client is responsible for making the callculations and routing requests to the correct cache
        - a light-weight library that is integrated in the service host
        - knows all cache servers
        - requires all cache clients to have the same list of servers
        - stores list of servers in sorted order, e.g., by hash value (`TreeMap` in java)
        - uses a binary search to id the server required; takes O(log(N)) time
        - uses UDP or TCP to talk to servers
        - treats an unavailable server as a cache miss 


            ```mermaid
            ---
            title: cache client
            ---
            flowchart LR
            subgraph service
            A[cache client]-.-B[cache server N]
            end
            C((user))-.-service
            A-.-D[cache server 1]
            ```


    * approaches to maintain a list of cache servers
        1. have said list in the service but outside the cache client using a CI/CD pipeline. is the simplest approach. requires configuration management tools, e.g. Puppet  and Chef, to deploy the list to every service host every time said list is modified. list has to be maintained manually


            ```mermaid
            ---
            title: list of cache server host names and ports on service host
            ---
            flowchart TD
            subgraph service_1
            A[cache client]
            B[list]
            end
            subgraph service_N
            C[cache client]
            D[list]
            end
            ```


        2. have the list on a dedicated storage, say, S3, that can be accessed by all service hosts. may require a daemon to run on every service host. said daemon pulls data from storage regularly. requires configuration management tools to deploy the list to every service host every time said list is modified. list has to be maintained manually 


            ```mermaid
            ---
            title: list of cache server host names and ports on common storage
            ---
            flowchart TD
            subgraph service_1
            A[cache client]
            end
            subgraph service_N
            B[cache client]
            end
            service_1--C[(storage)]
            service_N--C
            C--D[list]
            ```


        3. have a configuration service, e.g. ZooKeeper, to discover cache hosts and monitor their health. each cache host registers with the config service and sends *heartbeats* to the server regularly. said server's registration in the system is maintained as long as the *heartbeats* keep coming (think "continued protection" as long as the "protection money" keeps coming in). config service deregisters a server whose *heartbeat* fails to appear at the expected interval. every service host gets the list of registered (available) cache servers from config service. most expensive approach, however, everything is automated


            ```mermaid
            ---
            title:
            ---
            flowchart TD
            subgraph service_1
            A[cache client]
            end
            subgraph service_N
            B[cache client]
            end
            C[configuration service]--service_1
            C[configuration service]--service_N
            C--D[cache server 1]
            C--E[cache server 2]
            C--F[cache server N]
            ```


### acheving high availability
* method: [data replication][def4]
* approaches
    1. probabilistic protocols e.g. bimodal multicast
    2. consensus protocols &rarr; favour strog consistency
* leader-follower approach
    - a subset of the consensus protocol approach
    - one leader (master) cache, many follower (slave) caches; follower caches' objective is to be a replica of the leader
    - follower, automatically, tries to connect to leader when the connection between them breaks for whatever reason
    - follower caches live in different data centres
    - `PUT` requests from cache client go through the leader cache
    - `GET` requests are handles by the leader and closest-proximity follower cache


            ```mermaid
            ---
            title: leader-follower approach
            ---
            subgraph service
            A[cache client]
            end
            service--PUT, GET--B[leader]
            subgraph data_centre_1
            C[follower 1]
            end
            subgraph data_centre_2
            D[follower 2]
            end
            subgraph data_centre_N
            E[follower N]
            end
            B--data_centre_1
            B--data_centre_2
            B--data_centre_N
            service--GET--data_centre_2
            ```

    - leader cache is elected in one of two ways:
        1. dedicated leader cache
        2. have a configuration service that selects the leader based on a set of rules; a follower can be promoted when a leader is down or otherwise incapable


            ```mermaid
            ---
            title: select a leader - config service
            ---
            flowchart LR
            subgraph config_service
            A[node 1]--B[node 2]
            B--C[node N]
            c--A
            end     
            ```





[def]: https://math.libretexts.org/Courses/North_Hennepin_Community_College/Math_1120%3A_College_Algebra_(Lang)/06%3A_Trigonometric_Functions_of_Angles/6.03%3A_Points_on_Circles_Using_Sine_and_Cosine
[def2]: https://math.libretexts.org/Courses/City_University_of_New_York/College_Algebra_and_Trigonometry-_Expressions_Equations_and_Graphs/04%3A_Introduction_to_Trigonometry_and_Transcendental_Expressions/4.01%3A_Trigonometric_Expressions/4.1.04%3A_The_Unit_Circle
[def3]: https://en.wikipedia.org/wiki/Shard_(database_architecture)
[def4]: https://en.wikipedia.org/wiki/Replication_(computing)