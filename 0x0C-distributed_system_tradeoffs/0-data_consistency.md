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
    - limitations: cache replacement and miss
        - solution: multiple copies of data
        - that is, have all the data in all the servers
* having multiple copies of the same data solves two of our problems viz:
    - no single point of failure because users can connect to whatever working server that is nearest
    - no latency because users can access data from far away at the server closest to them
* how will all the servers have the same data?
    - there will be an update mechanism
    - said mechanism solves the consistency problem
* mechanisms to implement consistency
    1. manual updates when the product/service does not require frequent updates
        - example: banking. record transactions in the ledger then make updates to the necessary entities in due course
    2. use TCP to update servers regularly
        - TCP is reliable and data is ordered
        - update will not happen is the recipient server is down
        - we find ourselves with the [two generals' problem][def]
        - we can use the leader-follower strategy to solve said problem
            - set one server as the leader
            - said leader read and writes to the DB
            - the follower, simply, read from the DB
            - all `create`, `update` and `delete` requests are implemented by the leader
            - there will be inconsistencies whent he leader is down/out
        - another solution: two-phase commit strategy
            - simply an advanced  leader-follower strategy
            - one leader, many followers
            - leader sends a [prepared statements][def2] command/statement/request to the followers
            - followers send an `ACK` response to the leader; said response means "yes, leader, I have received the request"
            - leader asks followers to commit changes to mem/DB etc
            - followers send an `ACK` response to the leader; said response means "yes, leader, I have committed the changes you sent"
            - susceptibile to edge case limitations 18:13

[def]: https://en.wikipedia.org/wiki/Two_Generals%27_Problem
[def2]: https://en.wikipedia.org/wiki/Prepared_statement