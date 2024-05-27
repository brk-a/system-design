# 0x07-distributed_message_queue
* design a distributed message queue
### distributed message queue
* see [this article][def]
* TLDR: component that is, typically, used for inter-process communication (IPC) or for inter-thread communication within the same process. it implements an asynchronous communication pattern between two or more processes/threads; the sending and receiving party do not need to interact with the message queue at the same time. messages placed onto the queue are stored until the recipient retrieves them
### the problem
* say there are two services: *producer*, P, and *consumer*, C
* P and C need to communicate to each other
* we could set up synchronous comms; P sends a request to C and awaits a response
    - easy and quick to implement
    - single point of failure: C
    - need to figure out
        * what to do w. failed requests. re-try, perhaps?
        * how many requests are too much
        * how to deal w. C when it is slow
        * what to do if there are, for whatever reason, many Cs
* alternative: set up a service that uses asynchronous comms; it receives requests from P and relays it to one and only one C a short time after
    - such a service is called a *queue*
    - it is *distributed* because data is stored on several machines
    - do you see what we're doing here? *distributed ... queue*?
### requirements
#### functional
* create two APIs: `sendMessage(messageBody)` and `receiveMessage()`
    - these are the core APIs we require; the list is not exhaustive
    - the former is used by P to send messages to the queue
    - the latter is used by C to retrieve messages from the queue
#### non-functional
* scalable &rarr; handles increases in load gracefully (w/o downtime, ideally)
* available &rarr; withstands hardware and/or network failure
* performant &rarr; single digit latency for main ops
* durable &rarr; data, once submitted, is not lost
### high-level arch
* client P uses a virtual IP (VIP) to communicate w. client C
* VIP is a symbolic hostname e.g. mywebservice.domain.com; it resolves to a load balancer system
* load balancer routes P's request across a number of servers. P's request is forwarded to a FE web service
* FE web service is responsible for initial request processing e.g. validation, authentication etc. the queue's metadata e.g. creation date, time, owner etc are stored in a DB. said DB is hidden behind some fa&#199;ade, a metadata service
* BE web service is responsible for message processing and persistence

    ```mermaid
    ---
    title: high-level arch
    ---
        flowchart LR
        A((P))--send-->B[VIP]
        B---C[load balancer]
        C---D[front end]
        D---E[metadata service]
        E---F[(metadata)]
        D---G[back end]
        G---D
        F---E
        E---D
        D---C
        C---B
        H((C))--receive-->B
    ```

### in depth
#### VIP and load balancer
* load balancer allows the system to have high throughput and availability
    * client makes a request using the VIP
    * VIP resolves to a load balancer in the cluster of load balancers
    * load balancer directs the request to one of the FE hosts in the cluster of FE hosts
* what happens when load balancer goes down?
    * good question; it appears, at first, that the load balancer is a single point of failure
    * it is simple, actually: primary and secondary nodes
    * primary nodes accepts connections and serve requests; secondary nodes monitors the primary nodes
    * if, for whatever reason, a primary node is unable to accept connections, a secondary node takes over immediately
* what happens when the limits w.r.t. #requests and #bytes that a load balancer can process are reached?
    * this is a scale problem
    * solution: multiple VIPs aka multiple VIP partitioning
    * assign multiple records *A* records to the DNS for the VIP service
    * requests, therefore, are partitioned across several load balancers
    * spread the load balancers across several data centres to improve availability and performance

    ```mermaid
    ---
    title: VIP(s) and load balancer(s)
    ---
        flowchart LR
        A((P))---B[distributedmessagequeue.domain.com]
        B--VIP 1---C[load balancer 1]
        B--VIP 2---D[load balancer 2]
        B--VIP N---E[load balancer N]
        C---F[frontendhost1.domain.com]
        C---G[frontendhost2.domain.com]
        D---H[frontendhost3.domain.com]
        D---I[frontendhost4.domain.com]
        E---J[frontendhostN-1.domain.com]
        E---K[frontendhostN.domain.com]
    ```

#### FE service
* a lightweight web service
* has stateless service deployed across several data centres
* responsible for the following
    - request validation
        * require that all required params are present
        * data falls w/i the constraints set (is message size smaller than X size? etc)
    - authentication/authorisation
        * authentication: make sure that a user/service is who/what it says it is
        * in this case: make sure that P is registered in the system (does P's id match the one in the DB? etc) 
        * authorisation: make sure that a user/service is allowed to perform the action it wants to perform
        * in this case: make sure that P is, indeed, allowed to make requests to the FE service (does P have read/write/execute etc access to the FE service?)
    - TLS (SSL) termination
        * TLS termination: decrypt a request and pass on the unencrypted result to another service
        * in this case: decrypt requests from Ps and pass the unencrypted result to the BE service
        * said termination is not directly handled by the FE service; a TLS HTTP proxy that runs as a process on the same host does that
        * also, SSL on the load balancer is expensive, therefore, it is implemented on the FE service
    - server-side encryption
        * messages are encrypted as soon as the FE service receives them
        * messages are stored in encrypted format; FE only decrypts messages when they are sent to C
    - caching
        * stores copies of the sorure data
        * reduces load to BE service, increases overall throughput availability and decreases latency
        * stores metadata about the most actively used queues
        * stores identity information to save calls to the auth service
    - rate limiting(throttling)
        * rate limiting: capping the number of requests a client can make to the server per unit interval of time
        * in this case: capping the number of requests P makes to the FE service per unit interval of time
        * protects web service from being overwhelmed by requests (malicious or otherwise)
        * leaky bucket algorithm is a popular implementation of rate limiting
    - request dispatching
        * responsible for all activities associated with sending requests to BE services (client management, response processing, resource isolation, etc)
        * bulkhead pattern helps isolate elements of an application into pools such that if one fails the others carry on
        * circuit breaker pattern prevents an application from repeatedly trying to execute an operation that is likely to fail
    - request deduplication
        * may occur when a response from a successful `sendMessage()` request fails to reach a client
        * lesser an issue for *at-least-once* delivery semantics; a bigger issue for *exactly-once* and *at-most-once*
        * use caching to store previously-seen request IDs
    - usage data collection
        * gather real-time info that can be used for audit and billing
#### metadata service
* stores info about queues
* info about a queue is captured and stored when said queue is created
* metadata service is, simply, a caching layer for the FE; has a persistent storage
* supports many reads and relatively little writes
* strong consistency storage is preferred but not required
##### organising cache clusters: store the whole dataset in cluster nodes
* cache is relatively small
* FE host calls, at random, a metadata service host; does not matter which one because each has a copy of the whole data set
* possible to place a load balancer between the FE and metadata services because
    - the FE does not care which service it connects to
    - the metadata services have a copy of the whole data set

    ```mermaid
    ---
    title: store the whole dataset in cluster nodes
    ---
        flowchart TD
        A[FE]---B[metadata service]
        A---C[metadata service]
        A---D[metadata service]
        B--"A-Za-z0-9"---E[node 1]
        F[node 2]--"A-Za-z0-9"---G[(A-Za-z0-9)]
        H[node N]--"A-Za-z0-9"---G
        E---G
    ```

##### organising cache clusters: shard the dataset (FE is aware of shards)
* partition the data set into smaller chunks called *shards*
* the premise is this: data set is too large to to be placed into the memory of a single host
* each shard is stored in a separate node in the cluster
* FE host calls, using an algorithm, a metadata service host that contains the data set it requires
* metadata service hosts represent a consistent hashing ring

    ```mermaid
    ---
    title: shard the dataset (FE is aware of shards)
    ---
        flowchart TD
        A[FE]---B[metadata service]
        A---C[metadata service]
        A---D[metadata service]
        B--"A-Ha-h0-9"---E[shard 1]
        F[shard 2]--"I-Qi-q0-9"---G[(A-Za-z0-9)]
        H[shard N]--"R-Zr-z0-9"---E
        E---G
    ```


##### organising cache clusters: shard the dataset (FE is unaware of shards)
* partition the data set into smaller chunks called *shards*
* the premise is this: data set is too large to to be placed into the memory of a single host
* each shard is stored in a separate node in the cluster
* each metadata service is aware of the existence of other shards and can redirect a request to a different service
* FE host calls, at random, a metadata service host; said service may or may not contain the data the FE requires
* if metadata service does not have the data, it calls the service that contains the data set the FE requires
* metadata service hosts represent a consistent hashing ring

    ```mermaid
    ---
    title: shard the dataset (FE is unaware of shards)
    ---
        flowchart TD
        A[FE]---B[metadata service]
        A---C[metadata service]
        A---D[metadata service]
        B--"A-Ha-h0-9"---E[shard 1]
        C--"I-Qi-q0-9"---F[shard 2]
        D--"R-Zr-z0-9"---G[shard 3]
        B-.-C
        C-.-D
        B-.-D
        E---H[(A-Za-z0-9)]
        F---H
        G---H
    ```

#### back end service
* we must figure out
    * where and how to store messages
        - DB, perhaps? not a good idea because our system requires high throughput and fast, efficient read/write ops
        - memory, maybe? yes, that works, however, it must be a combination of a RAM and local disk of a BE host
        - file system? yes, this works too...
    * how to replicate data
        - replicate w/i a group of hosts, that is, send copies of messages to other hosts so that said messages can survive host hardware and/or software failures, if any
    * how FE selects a BE host to dend data to and where the FE knows where to retrieve the data from
        - leverage metadata service, perhaps? great idea 💡
* how it works
    * `sendMessage()`request comes to FE
    * FE consults metadata service on what BE host to send data to
    * data is sent to a selected BE host and replicated
    * `receiveMessage()` request comes to FE
    * FE consults metadata service on what BE host has the data `receiveMessage()` requires

    ```mermaid
    ---
    title: BE service high-level relationship to the rest of the system
    ---
        flowchart LR
        A((P))--sendMessage-->B[FE]
        B-.-C[metadata service]
        B-->D[BE host]
        E((C))--receiveMessage-->B
    ```

* how BE service will be configured
    1. leader-follower configuration &rarr; each BE instance/host is considered a leader of a particular set of queues
        - leader &rarr; all requests from a particular queue (say, `sendMessage()` or `receiveMessage()`) go to this leader instance
        - `sendMessage()` request comes to FE  service; say queue id is *q1*
        - FE service calls metadata service to identify a leader BE instance for said queue, say, instance B
        - FE service sends message to instance B
        - instance B replicates message to instances in its cluster
        - `receiveMessage()` request comes to FE service
        - FE service calls metadata service to identify a leader BE instance for said queue, say, instance B
        - FE service retrieves message to instance B; the message may be retrieved from any instance in the cluster, however, instance B, and instance B only, communicates with FE service
        - instance B cleans up the the original message and replicas

        ```mermaid
        ---
        title: BE service leader-follwer configuration
        ---
            flowchart LR
            A((P))--sendMessage-->B[FE service]
            B---C[metadata service]
            B---D[BE instance B]
            E[BE instance A]~~~D
            F[BE instance C]~~~D
            D---G[FE service]
            G---H[metadata service]
            I((C))--receiveMessage-->G
        ```

        - how do we elect the the leader? eea...sy! an *in-cluster manager*
            * in-cluster manager e.g. ZooKeeper is responsible for  maintaining a mapping between queues, leaders and followers

                |queue ID|leader host|follower hosts|
                |:---:|:---:|:---:|
                |q1|B|A, C|
                |q2|D|B, E|

            * in-cluster manager must be reliable, scalable and performant
            * creating one is quite the task; can we avoid building one? maybe... it requires that all instances be equal. we've seen that before, haven't we?
    2. small cluster of independent hosts &rarr; two ar three machines distributed across several data centres
        - `sendMessage()` request from P's FE service is forwarded to the closest, most available node of BE cluster
        - FE uses metadata service to determine which BE node the request will be sent to
        - BE instance is responsible for replication of data across all nodes in cluster
        - `receiveMessage()` request from FE is forwarded to the closest, most available node of BE cluster; metadata service is responsible for identifying said node
        - FE retrieves the message from the BE node and forwards it to C
        - selected node cleans up original message and replicas

            ```mermaid
            ---
            title: BE service small cluster of independent hosts configuration
            ---
                flowchart LR
                A((P))--sendMessage-->B[FE service]
                B---C[metadata service]
                B---D[BE node B]
                E[BE instance A]~~~D
                F[BE instance C]~~~D
                D---G[FE service]
                G---H[metadata service]
                G<--receiveMessage--I((C))
                C---J[out-cluster manager]
                H---J
            ```

        - we no longer require a component to elect a leader, however, we require a queue-to-cluster assignment manager
        - enter the out-cluster manager: it will maintain a mapping  between queues and clusters

            |queue ID|cluster ID|
            |:---:|:---:|
            |q1|c1|
            |q2|c2|
            |...|...|
            |qn|cn|

        * in-cluster assignment manager vs out-cluster assignment manager

            |paramater of comparison|in-cluster|out-cluster|
            |:---:|:---:|:---:|
            |what it manages|manages queue assignment w/i a cluster|manages queue assignment among clusters|
            |responsibility|maintains a list of hosts in the cluster|maintains a list of clusters|
            |system health|monitors "heartbeats" from hosts|monitors health of each cluster|
            |system failures|deals w. leader-follower failures|deals w. overheated clusters|
            |requests exceed capacity|splits queue between cluster nodes|splits queue between clusters|

        * use any or both as your project requires
### other considerations
* queue creation and deletion
    - queue can be auto-created when the first message is received by the FE service
    - alternative: have an API create a queue
    - the API way is superiror; it allows us more control over the queue creation parameters
    - delete queue operation is not as easy as it appears: do not expose `deleteQueue()` API method via  a pubblic REST endpoint
    - instead, expose it through a command line utility so that only experienced admin users may call it
* message deletion
    - option 1: fail to delete a message immediately after it was consumed
        - in this case, consumers are responsible for whatever they have consumed already
        - we must maintain a list or other sort of ordering of the messages in the queue and keep track of the offset, the position of a message in a queue. messages can then be deleted several days later by, say, a cron job
        - this is what Apache Kafka implements
    - option 2: fail to delete  a message immediately after it was consumed but mark it invisible so other consumers cannot retrieve it
        - consumer that retrieved the message must call `deleteMessage()` API method to delete the message from BE host
        - messages that are not explicitly deleted by consumers are visible to other consumers; they could be delivered or processed again and again
        - this is what Amazaon SQS implements
* message replication
    - option 1: synchronous replication
        - BE host waits until data is replicated to other hosts before returning a `success` status response to the producer client that sent the message
        - more durable than asychronous replication
        - has a higher latency cost for `sendMessage()` that asynchronous replication
    - option 2: asynchronous replication
        - BE host does not wait until data is replicated to other hosts before returning a `success` status; it returns said response as soon as the message is stored in a single BE host. the message is replicated to other  hosts afterwards
        - more performant than synchronous replication
        - does not guarantee that message will persist across replicas
* message delivery
    - three main message delivery guarantees
        - at most once &rarr; message is lost and may never re-delivered
        - at least once &rarr; message is never lost and may be re-delivered
        - exactly once &rarr; message is delivered once and only once
    - why do we need three? will anyone want anything other than the last one?
        - good questions...
        - they may not think they want the rest, however, they are not thinking; that is the problem
        - it is quite difficult to achieve exactly-once delivery in practice
        - there are many potential points of failure in a distributed message queue: P may fail to deliver or deliver multiple times, data replication may fail, Cs may fail to retrieve or process the message etc
        - most distributed message queue implementations support at-least-once delivery because it provides a balance between durability, availability and performance
* push vs pull
    - pull model &rarr; C sends `receiveMessage()` requests constantly; FE sends messages to C when they are available
        - easier to implement than push
        - from C's perspective, the process is inefficient; more work than in the push model
    - push model &rarr; C does not bombard FE w. `receiveMessage()` requests; C is, instead notified by FE as soon a s a message arrives at the queue. C then sends a `receiveMessage()` request
        - more difficult to implement than pull
        - from C's perspective, the process is efficient; `receiveMessage()` requests are sent only when necessary
* FIFO
    - First In First Out
    - oldest message in the queue is processed first
    - difficult to mainatain strict order in a distributed system; how do we solve this?
        - eea...sy! avoid the problem altogether
        - many implementations of distributed message queues do not guarantee a strict ordering of messages
        - those that do have limitations around throughput because a queue cannot be fast while processing many validation and coordination routines to guarantee a strict ordering of messages
* security
    - P's messages must be delivered securely to C
    - P &rarr; FE &rarr; BE &rarr; DB &rarr; BE &rarr; FE &rarr; C
    - encrypt messages in transit using SSL when using HTTPS
    - encrypt messages when storing then in BE hosts or DB
* monitoring
    - check components/microservices: FE, metadata and BE regularly to determine their health
    - track P's and C's experiences by providing them a way of tracking their queues
    - each service must emit metrics and write log data
    - said metrics and data are visualised on a dashboard; each service has its own dashboard
    - set up alerts for each metric in each service
    - give P and C the ability to set up alerts and dashboards
### final architecture

    ```mermaid
    ---
    title: distributed message queue
    ---
        flowchart LR
        A((P))--sendMessage-->B[VIP service]
        B-->C[load balancer]
        C-->D[FE service 1]
        D-.-E[metadata service]
        E-.-F[(matadata DB)]
        D-->G[BE service]
        H[FE service N]-->G
        C-->H
        B-->C
        C-->I((C))
    ```


[def]: https://en.wikipedia.org/wiki/Message_queue