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
        H((C))<--receive--B
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
        B--"A-Za-z0-9"---E[(A-Za-z0-9)]
        F--"A-Za-z0-9"---E
        G--"A-Za-z0-9"---E
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
        B--"A-Ha-h0-9"---E[(A-Za-z0-9)]
        F--"I-Qi-q0-9"---E
        G--"R-Zr-z0-9"---E
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
        B--"A-Ha-h0-9"---E[(A-Za-z0-9)]
        F--"I-Qi-q0-9"---E
        G--"R-Zr-z0-9"---E
    ```


[def]: https://en.wikipedia.org/wiki/Message_queue