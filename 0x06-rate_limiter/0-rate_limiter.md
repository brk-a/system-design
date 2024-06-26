# rate limiter
* design a rate-limiting system
### problem: noisy neighbour
* say we have a web app that, for one reason or the other, has become popular
* said app receives thousands of requests per second to the FE
* everything is alright until one of the clients (users) sends a lot more requests than normal
    - could be said client is another popular web app/service
    - could be a DoS or DDoS
    - could be that the client is running a load test
    - etc
* The situation where a client hogs a significant proportion of shared resources is called the *noisy neighbour problem*
    - therest of the clients experience higher latency and request failure rates
### requirements
#### overall
* have a system that limits the rate at which a client's requests are handled
    - say, a service that accepts three requests per second per client: this is called *throttling*
#### functional
* create a fn, `bool allowRequest(request)`, that takes in a request and returns a boolean. said boolean indicates whether or not said request is throttled 
#### non-functional
* low latency &rarr; make decision(s) asap
* accurate &rarr; throttle requests only when necessary
* scalable &rarr; supports an arbitrarily large #hosts in the cluster
#### why do we need a system?
* could we not, simply, write a software that scales to andle a high load?
    - glad you asked...
    - auto-scaling takes time; that time is all that is required to wreck the system
* why not implement max connections on the load balancer and max-thread-count on the service endpoint?
    - load balancer will, by definition, prevent too many requests to be directed at one service/server, however, its mechanism is indiscriminate: it cannot tell whether a request is resource-intensive or not, therefore, there is the strong probability of accepting all the resource-intensive requests at once. you can limit them at the application server level, not the load balancer level
* the problem does not appear to be a system design one; can we not throttle each host individually?
    - that works in the ideal/imaginary/theoretical world; this is the real world
    - say a load balancer distributes request evenly among the servers it sits in front of
    - say each request takes the same amount of time to fulfill
    - this is a single instance problem; there is no need for a distributed rate limiter
    - in the real world, however, load balancers hardly distribute loads evenly and some requests take longer than others to fulfill
    - also, each server behaves independently of the rest (no *iid* bullshit) 
### approach
#### single server
* throttle rules retreiver is in the service host; it fetches the rules the host uses to decide whether or not and how to throttle from the rules DB
* rules DB, which is outside the service host, is accessed through a service
* a request gets to the service host and is received by the client identifier builder
* said builder builds an identifier for the request (this is a request from client A, etc); think a combination of attributes that uniquely identify a client
* builder forwards the identifier to the rate limiter
* rate limiter checks identifier against rules in the throttle rules cache
    - match found: rate limiter checks whether #requests in the last interval (second, say) exceed the limit specified in the rules
        - excceds: queue or reject request
        - does not exceed: forward request to request processor
    - match not found reject request


    ```mermaid
        ---
        title: request processing for single server
        ---
        flowchart LR
        A(user)
        subgraph service_host
            A---B[client identifier builder]
            B---C[rate limiter]
            C---D[throttle rules cache]
            D---E[throttle rules retreiver]
            C-.allowed.-H[request processor]
            C-.not allowed.-I[reject]
        end
        E---F[rules service]
        F---G[(rules DB)]
        I-.code 503 or 429.-A
        I---J[queue]
        I---K[drop]
    ```

* there are three return codes
    - 503 (service unavailable) when identifier does not match the rules in the cache
    - 429 (too many requests) when #requests is above the theshold
    - 200 (OK) when all rules are satisfied
##### algorithmic approach to throttler: token bucket algo
* idea is to
* bucket has three attributes
    - capacity<sub>max</sub> &rarr; bucket has a max cap
    - tokens<sub>current</sub> &le; capacity<sub>max</sub> &rarr; current #tokens is less than or equal to the max cap (also, #tokens cannot be less than zero)
    - rate<sub>arrival</sub> = k &rarr; the rate of arrival of tokens is constant
* a token is taken from the bucket every time a request is made; request is denied/rejected when #tokens in bucket = zero

    ```mermaid
        ---
        title: token bucket
        ---
        classDiagram
        TokenBucket : +long maxBucketSize
        TokenBucket : +long refillRate
        TokenBucket : +double currentBucketSize
        TokenBucket : +long lastRefillTimeStamp
        TokenBucket : +allowRequest()
        TokenBucket : +refill()
    ```

* how the algo works
    - say at time t0 bucket A has 10 tokens
    - say that said bucket's capacity is 10 tokens and the refill rate is 10 tokens per second
    - say at time t1, which is t0 plus 300ms, a request that requires six tokens arrives
        - allowRequest(6)
    - the request is allowed because 6 &lt; 10
    - four tokens remain in the bucket when the request completes
    - say at time t2, which is t1 plus 200ms, a request that requires five tokens arrives
        - allowRequest(5)
    - `allowRequest()` adds two tokens to bucket; there are six tokens in the bucket now
        - see [0-rate_limiter.java][def]
        - ((t1+200) - t1) * 10 / 1e3 &rarr; 200ms * 10tokens/s &div; 1000ms = 2 tokens to add
        - `currentBucketSize` = min(4+2, 10) &rarr; minimum of the remaining tokens in bucket plus tokens to add and `maxBucketSize` = 6 tokens
    - the request is allowed because 5 &lt; 6
    - one token remains in the bucket when the request completes
    - say another reuest arrives at time t3, which is t2 plus 1000ms. the `refill()` function will set the `currentBucketSize` to 10 because min(10+1, 10) is 10
##### algorithmic approach to throttler: OOP method
* interfaces and classes
    * interface `JobScheduler` that schedules jobs. said jobs run at pre-determined intervals. the job is to retrieve rules from the rules service
    * interface `RulesCache` is responsible for storing rules in memory
    * interface `ClientIdentifier` creates a uniqe identifier for each client/request
    * inteface `RateLimiter` makes decisions
    * class `RetrieveJobScheduler` starts/stops the scheduler (e.g. ScheduledExecutorService) and runs `RetrieveRulesTask` periodically
    * class `TokenBucketCache` stores token bucket objects
        - Map, ConcurrentHashMap, Google Guava Cache etc
    * class `ClientIdentifierBuilder` retrieves client identity info from request context
    * class `TokenBucketRateLimiter` retrieves token bucket from cache and calls `allowRequest()` on the bucket
    * class `RetrieveRulesTask` makes a remote call to the `Rules` service, creates token buckets and loads said buckets into cache
* how it works
    - `RetrieveJobScheduler` runs `RetrieveRulesTask`
    - `RetrieveRulesTask` makes a remote call to a rules service
    - `RetrieveRulesTask`creates token buckets and places them in the `TokenBucketCache`
    - client request is forwarded to the `TokenBucketRateLimiter`
    - `TokenBucketRateLimiter` makes a call to `ClientIdentifierBuilder`
    - `ClientIdentifierBuilder` builds a uniqe id for the client/request
    - `TokenBucketRateLimiter` passes said unique id to `TokenBucketCache`
    - `TokenBucketRateLimiter` calls `allowRequest()` on the bucket


    ```mermaid
        ---
        title: token buckets using OOP
        ---
        flowchart LR
        A(User)--1-->B[TokenBucketRateLimiter]
        B<--2-->C[ClientIdentifierBuilder]
        B<--3-->D[TokenBucketCache]
        D<--E[RetrieveRulesTask]
        E<--F[RetrieveJobScheduler]
        E<-->G[rules service]
    ```

#### distributed approach
* say we have N hosts, M buckets and that our service can handle K requests per second per client. how many tokens should each bucket hold?
    - each bucket will have K tokens to begin with &rarr; see `refill` method at [0-rate_limiter.java][def]
    - requests from a host for the same key can, in theory, land at the same bucket, however, our system has a load balancer, therefore, it is not likely that said requests will land on the same bucket
* example: M = 3, N is finitely large, K = 4 and a load balancer exists
    - pick a host at random
    - one request goes to bucket 1; one token is consumed
        - {1: 3, 2: 4, 3: 4}
    - another request goes to bucket 3; one token is consumed
        - {1: 3, 2: 4, 3: 3}
    - two requests goes to bucket 2 w/i the one-sec interval; two tokens are consumed
        - {1: 3, 2: 2, 3: 3}
    - all four requests allowed have been used, however, there are tokens in the buckets
        - {1: 3, 2: 2, 3: 3}
    - there has to be a way the buckets can communicate w. each other
        - bucket 1 sees that three tokens have been used elsewhere, therefore, subtracts three from its remaining tokens (assuming #tokens left &ge; three)
        - bucket 2 sees that two tokens have been used elsewhere, therefore, subtracts two from its remaining tokens (assuming #tokens left &ge; two)
        - bucket 3 sees that three tokens have been used elsewhere, therefore, subtracts three from its remaining tokens (assuming #tokens left &ge; three)
    - there is a vulnerability: the system may process more than four requests because consensus among buckets takes time

    ```mermaid
        ---
        title: simple/naive distributed approach
        ---
        flowchart TD
        A[load balancer]---B[bucket 1]
        A---C[bucket 2]
        A---D[bucket 3]
    ```

* how do the buckets communicate?
    * glad you asked...
    * five ways: message broadcasting, gossip protocol, distributed cache, coordination service and random leader selection
    * message broadcasting &rarr; tell everyone everything. every bucket(host) knows everything about the rest. hosts may use a 3<sup>rd</sup> party service to discover each other and update themselves when a change occurs in one of the others

        ```mermaid
            ---
            title: message broadcasting
            ---
            flowchart TD
            A & B --- C & D
            A --- B
            C --- D
        ```

    * gossip protocol *(what!?)* &rarr; based on the way that epidemics spread. computer systems implement this using random peer selection

        ```mermaid
            ---
            title: gossip protocol
            ---
            flowchart TD
            A --- B 
            B --- C
            C --- D
            A --- D
        ```
    
    * distributed cache &rarr; see [distributed cache][def2]

        ```mermaid
            ---
            title: distributed cache
            ---
            flowchart LR
            A[host A] --- E[in-memory store eg Redis]
            B[host B] --- E
            C[host C] --- E
            D[host D] --- E
        ```

    * coordination service &rarr; chooses a leader; said leader coordinates the rest of the hosts

        ```mermaid
            ---
            title: coordination service
            ---
            flowchart TD
            A[host A] --- C[host C]
            B[host B] --- C
            D[host D] --- C
            E[coordination service] --- C
        ```

    * random leader selection &rarr; hosts choose a leader at random; may result in more than one leader

        ```mermaid
            ---
            title: random leader selection
            ---
            flowchart LR
            A[host A] --- B[host B] & C[host C] --- D[host D]
            A --- D
        ```
    
* what communication protocols will the buckets use?
    * TCP or UDP
    * you are certain that all data packets will not only be delivered but also that they will be delivered in order when using TCP; UDP is a different story
    * UDP is faster than TCP
    * UDP is faster but less accurate than TCP; make your choice
#### integrate rate limiter w. service process
* two ways:
    1. rate limiter in service process inside service host
    2. rate limiter client in service process that talks to rate limiter process. all of these are in the service host
* rate limiter in service process inside service host
    * rate limiter is a collection of classes that are integrated into service process
    * faster and is not affected by inter-process call failure
    * rate limiter process uses parent service's memory space

        ```mermaid
            ---
            title: rate limiter in service process inside service host
            ---
            flowchart TD
            subgraph service host
                subgraph service process
                    A[rate limiter]
                end
            end
        ```

* rate limiter client in service process that talks to rate limiter process
    * there are two libraries: the rate limiter itself and the rate limiter client
    * said client is integrated w. service process and  is responsible for inter-process calls between the rate limiter and the service process
    * slower and prone to inter-process call failure
    * programming language agnostic (daemon can be written in any language as long as it works as it should)
    * rate limiter process uses its own memory space
    * makes it easier to deal w. service team's paranoia


        ```mermaid
            ---
            title: rate limiter client in service process
            ---
            subgraph service host
                subgraph service process
                    A[rate limiter client]
                end
                A<-->B[rate limiter process]
            end
        ```

#### FAQs
* my service is popular proper; millions of users at peak time. does this mean millions of buckets are stored in memory?
    * in theory, yes; it is possible that millions of buckets will be created in memory
    * in practice, not likely. say millions of clients send requests at the same time (the same second); we will create millions of buckets in mem. the bucket will be maintained as long as the client that caused it to be made keeps sending requests within the allowed time interval, *k*. it is unlikely that said client will make said requests
* daemon (the rate limiter) may fail so that hosts in cluster fail to see said daemon. what now?
    * the host w. a failed daemon leaves the group and throttles requests w/o talking to other hosts in the cluster
    * nothing ugly happens; simply, less requests, in total, will be throttled
* what happens during a network partition when several hosts in a cluster cannot broadcast messages to the rest of the group?
    * *nada*; hosts in a network carry on as though nothing happened
    * hosts which cannot broadcast messages leave the group and throttle requests w/o talking to other hosts in the cluster
    * nothing ugly happens; simply, less requests, in total, will be throttled
* will configuration rules not be a nightmare to manage?
    * matter of fact, no
    * we may need to introduce a self-service tool that allows service teams to create, update and delete rules as needed
    * synchronisation will be implemented in the token buckets and token bucket cache; of course, we can use atomic references or concurrent hash maps, for example, to implement thread safety
    * caveat: synchronisation may become a bottleneck for services with unusually large requests per second rate
#### what should clients of our service do with throttled calls?
* glad you asked...
    * clients may
        1. queue and re-send said requests later
        2. re-try throttled requests in a *smart way* (exponential back-off and jitter)
            * wtf is exponential back-off and jitter?
                * good question...
                * idea is this: try requests at exponentially increasing waiting intervals. you realise that the intervals could get infinitely large and the requests would never end (because the interval never ends); this is where *back-off* comes in. back-off is a ceiling; a max value above which the interval cannot be. *jitter*, simply, adds randomness to the intervals to spread out the load; w/o jitter, the back-off algo will re-try at the same interval
                * TLDR: re-try while waiting randomly longer with each re-try until such a time as the waiting time excceds a set maximum

                ```mermaid
                    ---
                    title: big picture
                    ---
                    flowchart LR
                    subgraph service host
                        subgraph service
                            A[rate limiter client] --- B[client identifier builder]
                        end
                        subgraph rate limiter
                        C[rate limiter] --- D[throttle rules cache]
                        D --- E[throttle rules retriever]
                        end
                        C --- A
                        C --- I[message broadcaster]
                    end
                    F[rules service] --- G[(rules DB)]
                    F --- E
                    F --- G[rules console]
                    G --- H((service owner))
                    I --- J[other hosts in cluster]
                ```


[def]: ./0-rate_limiter.java
[def2]: ../0x03-distributed_caches/