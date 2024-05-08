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
    A(user)
    flowchart LR
    subgraph service_host
    A---B[client identifier builder]
    B---C[rate limiter]
    C---D[throttle rules cache]
    D---E[throttle rules retreiver]
    C-.allowed.-H[request processor]
    C-.not allowed.-I[reject]
    end
    E---F[rules service]
    F---G(rules DB)
    I-.code 503 or 429.-A
    I---J[queue]
    I---K[drop]
    ```

* there are three return codes
    - 503 (service unavailable) when identifier does not match the rules in the cache
    - 429 (too many requests) when #requests is above the theshold
    - 200 (OK) when all rules are satisfied