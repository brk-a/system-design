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
        B--receive-->H((C))
    ```

### approach
* 


[def]: https://en.wikipedia.org/wiki/Message_queue