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
    ```