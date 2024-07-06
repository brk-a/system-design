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
            - leader sends a [prepared statements][def2] directive/command/statement/request to the followers
            - followers send an `ACK` response to the leader; said response means "yes, leader, I have received the request"
            - leader asks followers to commit changes to mem/DB etc
            - followers send an `ACK` response to the leader; said response means "yes, leader, I have committed the changes you sent"
            - susceptibile to edge case limitations
        - two-phase commit works viz:
            - phase 1, prepare: leader sends a `BEGIN` directive to DB (directly or through a message queue e.g. Kafka). leader sends the prepared statements mentioned above to DB. DB/message queue sends an `ACK` response (the first `ACK` mentioned above) to leader
            - phase 2, commit: leader sends a `COMMIT` directive to DB. said DB commits the transaction(s). DB/message queue sends an `ACK` response (the second `ACK` mentioned above) to leader
            - say leader does not get the first `ACK` response. said leader considers the transaction to have failed; the leader and DB perform a `ROLLBACK`. followers do what the leader says, therefore, they will roll back too
            - say the leader does not get the second `ACK` response. recall that TCP allows retries, therefore, the leader will retry the commit w/i the parameters of the system TCP config. the specific row being affected will be read-and-write-locked on the leader and read-locked on the followers and DB
            - the system is now consistent but unavailable
        - another solution: eventual consistency
            - eventual consistency implements the property of BASE (Basically-Available, Soft-state, Eventually-consistent)
### strong vs eventual consistency
* strong consistency is a consistency model used in concurrent programming (e.g., in distributed shared memory, distributed transactions etc)
    - a protocol is said to support strong consistency if:
        1. all accesses are seen by all parallel processes (or nodes, processors, etc.) in the same order (sequentially)
    - that is, only one consistent state can be observed, as opposed to weak consistency where different parallel processes (or nodes etc.) can perceive variables in different states
    - the transaction either succeeds or fails; no in-between: this property is called _atomicity_; it facilitates and maintains consistency of data in the system
    - strong consistency may implement ACID (Atomicity, Consistency, Isolation, Durability)
    - more info [here][def3]
* eventual consistency is  a consistency model used in distributed computing to achieve high availability that informally guarantees that if no new updates are made to a given data item, eventually, all accesses to that item will return the last updated value
    - eventual consistency, also called optimistic replication, is widely deployed in distributed systems
    - a system that has achieved eventual consistency is often said to have converged or achieved replica convergence
    - eventual consistency is a weak guarantee – most stronger models, like linearisability, are trivially eventually consistent
* eventually-consistent services are often classified as providing BASE semantics in contrast to traditional ACID
    - in chemistry, a base is the opposite of an acid, which helps in remembering the acronym
    - **basically-available** &rarr; reading and writing operations are available as much as possible (using all nodes of a database cluster) but might not be consistent (the write might not persist after conflicts are reconciled and the read might not get the latest write)
    - **soft-state** &rarr; without consistency guarantees, after some amount of time, we only have some probability of knowing the state since it might not yet have converged
    - **eventually-consistent** &rarr; if we execute some writes and then the system functions long enough, we can know the state of the data; any further reads of that data item will return the same value
* eventual consistency is sometimes criticised as increasing the complexity of distributed software applications. this is partly because eventual consistency is purely a liveness guarantee (reads eventually return the same value) and does not guarantee safety: an eventually consistent system can return any value before it converges
* more info [here][def4]
##### why bother comparing strong and eventual consistency?
* there is a trade-off between between performance, availability, reliability, and
    - strong consistency achieves high latency (poor performance), high reliability, neither high nor low functional correctness and an unpleasant ~~aka shit~~ UX
    - eventual consistency achieves low latency, neither high nor low reliability, neither high nor low functional correctness and a somewhat pleasant UX 4:20

[def]: https://en.wikipedia.org/wiki/Two_Generals%27_Problem
[def2]: https://en.wikipedia.org/wiki/Prepared_statement
[def3]: https://en.wikipedia.org/wiki/Strong_consistency
[def4]: https://en.wikipedia.org/wiki/Eventual_consistency