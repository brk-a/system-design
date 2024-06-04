# notification system
* design a notification system
### the problem
* web services send messages in reaction to an event
* examples
    - notify a card holder when transaction amount exceeds transaction limit
    - notify  the on-call engineer when service monitoring system encounters a large amount of faults produced by an API
* generally: say there is a service, P, called Publisher that produces messages which must be delivered to a group of other services, S, called Subscribers. we can set up synchronous communication between P and S such that P calls each S in some order and awaits a response. Bad idea. this introduces a number of challenges: it is difficult to scale when S &rarr; &infin; and/or #messages &rarr; &infin;. also, it is difficult to extend such a solution to support different types of S
* what if we had a system that register an arbitrarily large number of Ps and Ss, coordinate message delivery between them, be fault tolerant and be scalable; this system is the notification system we must build

    ```mermaid
    ---
    title: notification system concept
    ---
        %%{init: {"flowchart": {"htmlLabels": true}} }%%
        flowchart LR
        A[P]-->B[notification service]
        B-->C["`S<sub>1</sub>`"]
        B-->D["`S<sub>2</sub>`"]
        B-->E["`S<sub>N</sub>`"]
    ```

#### functional requirements
* create three APIs
    - `createTopic(topicName)` &rarr; creates a new topic
    - `publish(topicName, message)` &rarr; publishes a message to a topic
    - `subscribe(topicName, endpoint)` &rarr; allows S to receive messages from a topic
    - a topic is a named resource to which messages are sent; think of it as a bucket that stores messages from a publisher. all S receive a copy of the message from the bucket
#### non-functional requirements
* scalable &rarr; supports an arbitrarily large number of topics, Ps and Ss
* available &rarr; survives hardware/network failures; no single point of failure
* performant &rarr; keeps end-to-end latency as low as possible
* durable &rarr; messages must not be lost; each S must get each message at least once
### high-level architecture
* all requests from P will go through a load balancer for performance reasons
* a FE service will perform initial request processing
* there will be a DB to store info about topics and subscriptions
* said DB will be behind a metadata service for two reasons
    - seperation of concerns principle &rarr; provide access to DB using a well-defined interface
    - said service acts a a cache layer between DB and other services; we want to minimise the #hits to the DB (as few hits with every message published as possible)
* messages are stored in the temporary storage service for, well, a short time
    - the time in question depends on subscribers: seconds if all Ss are  available and message is sent successfully to them, several days at most otherwise
* Ss get messages through the sender service
* sender service gets messages from temporary storage
* we, simply, need to store all the info generated when `createTopic` and `subscribe` are called

    ```mermaid
    ---
    title: notification system high level architecture
    ---
        flowchart LR
        A((P))--publish-->B[load balancer]
        B-->C[FE service]
        C-.-D[metadata sevice]
        D-.-E[( metadata DB)]
        C-->F[temporary storage service]
        F-->G[sender service]
        G-.-C
        G-->H((S #1))
        G-->I((S #2))
        G-->I((S #N))
    ```

### approach
#### FE service
* stateless, lightweight web service
* deployed across several data centres
* responsible for
    - request validation
    - authentication and authorisation
    - TLS (SSL) termination
    - server-side encryption
    - caching
    - rate limiting
    - request dispatching
    - request deduplication
    - usage data collection
* FE service has
    - reverse proxy that picks up requests when they land on the host
        - reverse proxy is a lightweight server that is responsible for
            - SSL termination &rarr; HTTPS requests are decrypted and passed further in unencrypted form; responses are encrypted when being  sent to client
            - compression &rarr; e.g. with `gzip`; proxy compresses responses when being sent to client
    - FE web service that is responsible for
        - calling the metadata service to get info about the topic
            - may implement a local cache to minimise calls to metadata service
        - logging information about service health, exceptions raised in the course of operation, metrics(#requests, #faults, call latency data etc), audit logs (e.g. who made which request to what API when) 

    ```mermaid
    ---
    title: FE service host
    ---
        flowchart LR
        A((P))~~~I[]
        subgraph FE-service-host
        A--request-->B[reverse proxy]
        B--->C[FE service]
        C---D[cache]
        C---E[(local disk)]
        E---F[service logs agent]
        E---G[metrics agent]
        E---H[audit logs agent]
        end
        J[metadata service]---C
        K[service logs service]---F
        L[metrics service]---G
        M[audit logs service]---H
    ```

#### metadata service
* a distribted caching layer between the FE and a persistent storage
* supports many reads and few writes
* info about topics is divided among hosts in a cluster
* cluster represents a consistent hashing ring; eac FE host calculates a hash, say, MD5 or RSA, using a key, say, a topic name and topic owner identifier
* FE host picks a metadata host based on the hash value

    ```mermaid
    ---
    title: metadata service host consistent hashing ring arrangement
    ---
        flowchart LR
        A[A-Ga-g]---B[H-Nh-n]
        B---C[O-To-t]
        C---D[U-Zu-z]
        D---A
    ```

* how do FE hosts know which metadata service host to call?
    * good question...
    * two options...
    * one: central registry
        - introduce a component/service that is responsible for coordination
        - knows everything about all metadata service hosts
        - each of the said hosts sends a *"pulse"* regularly
        - each FE host asks the coordination service how to get to the metadata service host that contains the data required by the request
        - coordination service becomes aware of changes and re-maps hash key ranges every  time we add metadata hosts to the metadata service

        ```mermaid
        ---
        title: metadata service host coordination service arrangement
        ---
            flowchart LR
            A[A-Ga-g]---B[H-Nh-n]
            B---C[O-To-t]
            C---D[U-Zu-z]
            D---A
            E[coordination service]---A
            E---B
            E---C
            E---D
            F[FE host]---E
            F-.-A
        ```

    * two: gossip protocol
        - no coordinator service
        - every FE host is able to obtain info about all metadata service hosts
        - evry FE host is notified when metadata service hosts are added to or removed from the cluster
        - gossip protocol is based on the way epidemics spread: computers implement this with a form of *"random peer selection"*
        - w/i a given frquency, a machine picks another machine at random and shares data with it

        ```mermaid
        ---
        title: metadata service host gossip protocol arrangement
        ---
            flowchart LR
            A[A-Ga-g]---B[H-Nh-n]
            B---C[O-To-t]
            C---D[U-Zu-z]
            D---A
            E[FE host]---A
            E---B
            E---C
            E---D
        ```

#### temporary storage service
* fast, highly-available and scalable web service
* must guarantee data persistence
    - has to store messages for several days just in case S is unavailable
* several options
    - databases
        - no need for ACID-compliant transactions, complex dynamic queries or analytics and/or warehousing
        - we require a DB that is highly available, scales easily for reads and/or writes and tolerates network partitions
        - a NoSQL DB is best placed for this use case
        - messages have a limited size, say, &lt; 1Mb, therefore, we do not need a document store
        - no specific relationship between messages, therefore, no need for graph-type DBs
        - that leads to one of two NoSQL DB types: key-value and column
        - specific examples: Apache Cassandra, Amazon DynamoDB
    - in-memory storage
        - it better possess persistence
        - example: Redis
    - message queues
        - they fulfill all the requirements of the temporary storage service
        - more info [here][def]
        - example: Apache Kafka, Amazon SQS
#### sender service
* uses the *fan-out* method
* sender component retrieves message from temporary storage service using an in-built message receiver service
    - said service uses a pool of threads; each thread reads data from temporary storage service
    - naive approach: always start a predetermined number of message retrieval threads. some threads may be idle when the #messages &gt; #threads. conversely, the only way to scale will be to add sender hosts to the cluster
    - better approach: use the #threads required: no more and no less. keep track of #messages and #threads; adjust #threads accordingly. solves the scaling problem and also solves the problem where sender service bombards the temporary storage service with too many requests
    - use counting semaphore to restrict the #read message threads
        - a semaphore contains a set of permits; a thread must acquire a permit before it retrieves the next message. it must return said permit to semaphore to allow another thread to pick up the permit
        - #permits can be adjusted dynamically to match the load in the temporary storage service or achieve a desired read rate
* message reciever service talks to the metadata service through the message-sender client service to obtain info about S
* message-sender client sends the messages and metadata to the task-creator service. task-creator service creates independent tasks; each task is responsible for sending a message to one S and nothing else. this way, we deliver messages in parallel and a single bad/failed delivery does not affect the rest
* task creator service send the tasks tasks to the task-executor service; this service, well, executes the tasks
    - in java, for example, the task-creator and task-executor services could be instances of the `ThreadPoolExecutor` class
    - use semaphores to track #threads in the pool
    - say we have enough threads to process the newly created tasks; we, simply, submit all tasks for processing
    - say we do not have enough threads to process said newly created tasks; we, simply, postpone or stop the excess tasks from being processed and return the message(s) to the temporary storage service. a different sender service may pick up the message(s) so that the process begins again
    - tasks may delegate actual delivery of message to other microservices e.g. SMS microservice

    ```mermaid
    ---
    title: sender service
    ---
        flowchart LR
        subgraph sender-service
        A[message retriever]-->B[MS client]
        B-->C[task creator]
        C-->D[task executor]
        D-->G((task 1))
        D-->H((task 2))
        D-->I((task N))
        end
        E[temporary storage]---A
        F[metadata service]-.-B
        J["`S<sub>1</sub>`"]--call HTTPS endpoint---G
        K["`S<sub>2</sub>`"]--send email or SMS---H
        L["`S<sub>3</sub>`"]--mobile push---I
    ```

#### what else may come up
* did we just build a solution for spammers?
    - yes and no
    - yes, spammers can use this solution to, well, spam
    - no, our system will register Ss. all Ss must confirm that they agree to get nootifications from our service using an email or HTTPS endpoint
* how do you handle duplicate messages?
    - FE service catches any/all duplicate messages sent by publishers
    - Ss are responsible for avoiding duplicate messages that occur when there are re-tries caused by network failure or Ss' internal failures
* if re-tries cause duplicate messages, why re-try?
    - re-tries are one of the ways that guarantee that messages will be delivered at least once
    - we have the option to send undelivered messages to a different S or store the undelivered messages in a system that Ss monitor; both options are inefficient for the goal at hand
    - would be great if our notification system provides a way for subscribers to define re-trying behaviour (re-try policy e.g. what to do when message cannpt be delivered after re-try limit is reached)
* does our system guarantee message order e.g FIFO, LIFO etc?
    - no. our system does not guarantee message order
    - say messages are processed w. some attribute that preserves the order e.g. sequence number or timestamps: delivery of messages does not honour this because tasks are executed in any order
    - slower sender hosts may fall behind or message delivery attemp may fail meaning re-tries will arrive in an unpredictable order
* how do we implement security?
    -


[def]: ../0x07-distributed_message_queue/0-distributed_message_queue.md