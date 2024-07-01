# data consistency
* a user's data must remain the same no matter how many servers are added or removed from the cluster
    - user data in server 1 = user data in server 2 ... = user data in server N where N is the number of servers in the cluster
### single node problem
* a system that runs on a single node is vulnerable to the following problems
    - single-point-of-failure scenarios
    - vertical scaling limits
        - high cost
        - scaling becomes impossible at a point
    - high latency
* possible solution: have N servers in N locations that do not talk to each other
    - users access the server that is closest to them
    - there are trivial limitations
        1. servers do not have the same data
        2. a user cannot access users that are not connected to the server that is local to said user
    - possible way to overcome limitations is to allow users to connect to the server that contains the data that they need, however, this is not efficient. also, it does not solve the first and last problems above
    - possible way to overcome high-latency-problem is to cache data  from over servers. users connect to a server that is local to them and access the cached data; fetch once serve many; this, however, does not eliminate latency
    7:06