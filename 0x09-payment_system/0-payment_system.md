# payment system
* create a system that allows a buyer to pay for goods/services on an eCommerce website
### the problem
### requirements
#### functional
* payment system that uses a PSP e.g. [Daraja API][def] or stripe
    - alternative: system that connects directly to card schemes
        - must comply with PCI DSS level 1, PSD 2, KYC and AML
    
#### non-functional
* reliability
    - business level
        - reconciliation
        - paymment status
        - handle delays
    - technical level
        - redendancy
        - persistent queues
        - retry strategies
        - idempotency
        - fault tolerance
* correctness
* availability
* scalability
### high-level view
* customer places an order with merchant's website
    - customer provides payment information
    - merchant site sends customer to pay site (which has a form page)
* pay site sends request to payment gateway
    - pay site must conform to PCI-DSS, GDPR etc
* payment gateway sends data to risk check service
    - yes, this is a risky operation: drop request
    - no this is not a risky request: carry on
* payment gateway sends data to acquiring bank's API gateway
    - acquiring bank processes card payments on behalf of the merchant
* acquiring bank's API sends data to card schemes service
    - captures txn info
    - performs basic validation
    - routes the request along the appropriate card schemes service
* card schemes service sends the payment info to the issuing bank's API
* issuing bank approves or decline the payment
    - more validity checks
    - whether or not customer has sufficient balance
    - account is in good standing (e.g. credit card payments are done on time etc)
    - this is sent back in the response

    ```mermaid
    ---
    title: high level view of payment system
    ---
        flowchart LR
        A((customer))--places and order-->B[merchant website]
        subgraph payment-service-provider
        B--payment form-->C[payment gateway]
        C-.fraud prevention.-D[risk checking service]
        C-->E[acquiring bank]
        end
        E-->F[card schemes service]
        F-->G[issuing bank]
        G-.response.->F
        F-.response.->E
        E-.response.->C
        C-.response.->B
        B-.response.->A

    ```
### system components

    ```mermaid
    ---
    title: payment system components
    ---
        flowchart LR
        A((customer))--payment event-->B[payment gateway]
        subgraph payment-service
            B-->C[payment service]
            C-.-D[PSP integration]
            E[wallet]
            F[ledger]
        end
        B-.-G[(DB)]
        subgraph PSPs
            I[Daraja API FE]
            J[stripe FE]
            K[etc]
        end
        D--payment details-->PSPs
        subgraph card-schemes
            L[Visa]
            M[Mastercard]
            N[etc]
        end
        PSPs-->card-schemes
        PSPs--response-->payment-service
        C--keep track of account balance etc---E
        E-.-O[(DB)]
        C--updates transaction information---F
        F-.-P[(DB)]
    ```

### asynchronous communication
* sync vs async
    - synchronous comms &rarr; a client/service sends a request to a server/service and waits for a response before sending another
    - asynchronous comms &rarr; a client/service sends a request to a server but does not wait for a response before sending another
* facts on the ground
    - hardware and/or software can fail at any time
    - networks can fail or be slow
    - many moving parts: services, agents, servers, DBs etc
* sync comms is not tolerant to failure or latency
    - also does not isolate failure; the system, overall, becomes less available
    - exposes system to risk of cascading failure
    - does not provide loose coupling of components
* use sync comms only when necessary
* async comms is suited for loosely coupled components, traffic spikes
    - allows services e.g. Apache Kafka to queue requests and send them to the server(s) at the proper rates
    - allows server to scale with the #requests in the background
* async comms solves the fault tolerance and latency constraints
    - best  for payment processing, fraud detection and analytics
### reliability

    ```mermaid
    ---
    title: "reliability" 
    ---
        flowchart TD
        A[reliability]---B[business level]
        A---C[technical level]
        B---D[reconciliation]
        B---D[payment status]
        B---E[handle delays]
        B---F[...]
        C---G[redundancy]
        C---H[persistent queues]
        C---I[retry strategies]
        C---J[idempotency]
        C---K[fault tolerance]
        C---L[...]
    ```

#### types of failure
* network and server failures
* poison pill errors
    - inbound mesage cannot be processed/consumed
* functional bugs
    - no technical errors, however, results are invalid

    ```mermaid
    ---
    title: failures
    ---
        flowchart TD
        A[failures]---B[system failures]
        A---C[poison pill errors]
        A---D[functional bugs]
    ```

#### guaranteeing transaction completion
* use a messaging queue e.g. Apache Kafka to
    - make sure that messages are not lost in the network
    - guarantee said messages are received assuming that services may break at random
* message is stored on message queue until a success response from the receiver service/server is received
* receiver service/server stores message in DB before sending te success response to message queue
* this way, message is stored on at least one disk; first guarantee done ::white tick::
* message queue may resend messages regularly or the receiver service/server may poll the message queue regularly
* this way, receiver service/server will always get the messages; second guarantee done ::white tick::
    
    ```mermaid
    ---
    title: "message queue to guarantee transaction completion"
    ---
        flowchart LR
        A-->|payment update| B[payment service]
        B-->|create event| C[apache kafka]
        C-->|consume message| D[wallet service]
        C-->|consume message| E[ledger service]
        D-.-|offset: 1| F[(DB)]
        E-.-|offset: 1| G[(DB)]
        D-.-|success| C
        E-.-|success| C
    ```

#### transient failures
* we may need to get info from other services in the course of making a payment/transaction
    - e.g. result s of a DB query
* a message queue is not efficient
    - payment requests may fail because of network issues etc that have nothing to do with either service
* how do we treat transient errors?
    - glad you asked...
    - three ways to start with
        1. retry strategies
        2. timeouts
        3. fallbacks
* retry strategies &rarr; payment service makes the pay request regularly until it receives a response from the, say, risk-check service
    - works when network errors are the cause of the failure
    - retry parameters
        - #retries (n) &rarr; you want to limit the number of retries to, say, five per IP address per day, else, you expose the system to attacks like [this one][def2]
        - interval (t) &rarr; strategies
            1. immediate (t&rarr;0) &rarr; retry immediately after failure; almost certainly won't work because it is almost certain that the problem has not been resolved in such a short time
            2. fixed interval(t=*k* where *k* is a constant) &rarr; retry every *k* long until a response is received
            3. incremental intervals (t<sub>i</sub>=*t<sub>i-1</sub> + k* where *k*&gt;0) &rarr; retry every *t* long. the next *t* is always longer than the last 
                - alternative: t=*f(t)* where *f(t)* is a linear function (f(t) = a + bt)
            4. exponential back-off intervals (t=f(t)) where *f(t)* = ab<sup>t</sup>, t&gt;1 a&gt;0 and b&ne;1
                - the function f(t) = 2<sup>t</sup> is used almost everywhere
                - retry after 2<sup>t</sup> time where t = 1, 2, 3 ... until a response is received
            5. random interval (t=f(t)) where *f(t)* follows any probability distribution, preferably, poisson
* timeouts &rarr; idea is to avoid unbounded waiting times for a response
    - *min(t)* where 0&lt;t&lt;n, n&lt;&infin;
    - operation is aborted when time to respond is too high; request is treated as failed
    -  say a user sees that the order was not processed. said user cannot know whether
        1. the payment was successful but the response was timed out
        2. the request is still being processed in the payment system (request timed out while payment was in progress)
        3. the request did indeed reach the payment system
    - user may decide to restart the order; that means the user may pay twice for the same order and such other undesirable outcomes
    - how big should we set the timeout?
        - depends on each endpoint; set the upper bound  of each timeout to allow laggard requests to arrive and the lower bound to time out responses that may never arrive
* fallbacks &rarr; enable a service to execute/process requests even when requests to another service/server  it depends on are failing
    - say the fraud check service is not available for whatever reason. payment service, which depends on the response from the fraud check service has two options
        1. abort the whole request computation (in a similar manner to atomicity principle in ACID)
        2. take a fallback rule in memory and carry on
            - this is a compromise between risk to and availability of the system

            ```C
                ...
                double threshold = X;
                if (payment<threshold){
                    // carry on
                } else {
                    // abort abort abort
                }
                ...
            ```


            ```mermaid
            ---
            title: fallback
            ---
                flowchart LR
                A((user))-->B[website]
                B-->C[payment service]
                C--xD[fraud check service]
                C-->|fallback rule| C
            ```

#### persistent failures
* say the fraud check service from the example above is unavailable for a significant amount of time, say, two minutes; what now?
    1. abort the request assuming failure is acceptable
    2. save messages in a dedicated queue to debug later when dealing with poison pill errors
        - this pattern is called the *dead letter queue* method
    3. save messages in a dedicated, persistent queue when dealing with a broken service; requests will be retried when the service is available

        ```mermaid
        ---
        title: fallback
        ---
            flowchart LR
            A((user))-->B[website]
            B-->C[payment service]
            C--xD[fraud check service]
            C-->|dead letter queue| E[dedicated message queue]
            C-->|normal flow queue| F[persistent message queue]
        ```

### idempotency
* allows us to charge the customer once and only once for one transaction
    - avoid double payments
* say a payment fails for whatever reason; there should be a way to safely retry the payment w/o charging the customer again
* an idempotent op, from an API perspective, is one that has no additional effect when it is called more than once w. the same parameters
* say that a KES 10.00 transaction is initiated by a customer. it goes through the payment service to the PSP successfully, however, the response from the PSP fails for whatever reason
    - payment service does not know whether the transaction is successful or not; it returns false `fail` response to the customer
    - customer, being customer, will, almost certainly, click the `pay` button again or retry the payment
    - how do we avoid charging the customer twice?
        - eea...sy! idempotent key
        - an idempotent key  is a unique value that is generated by the client and expires after a certain amount of time
        - said key is the value to the `idempotency-key` key in the payment request's HTTP header

            ```javascript
                ...
                idempotency-key: b012cf6f-5cfe-44b7-bb06-780c54013029
                ...
            ```

        - UUIDs are, typically, used as idempotent keys; also highly likely that said key is the payment order id
        - the payment service checks the payment order id and identifies it as a payment order that had been made but not fulfilled; in other words, a retry operation
        - the unique key constraint of any DB is sufficient to enforce idempotency at PSP level
        - all payment requests are inserted into DB, however, the unique constraint will cause a retry operation payment order to fail because it had been inserted before
        - a successful insertion, therefore, means that the payment had not been fulfilled; charge the customer
        - an unsuccessful insertion, conversely, means that the payment had already been fulfilled; do not charge the customer
        - with an unsuccessful insertion, we can return the latest status of the request
        - only one request is processed when multiple, concurrent requests w. the same idempotency key are detected; the rest receive a `429: Too many requests` response

    ```mermaid
    ---
    title: idempotency
    ---
        flowchart LR
        A((customer))-->|10 + UUID| B[payment service]
        B-->|10 + UUID| C[PSP]
        C-->|10 + UUID| D{UUID seen before?}
        D--x|yes| E[fetch latest status from DB]
        D-->|no| F[(DB)]
        F-->|latest status from DB| C
    ```

### distributed systems
* allows the system to scale
#### redundancy
* achieved using replication
* idea is to eliminate single points of failure
* copies of data and/or processes are stored on multiple DBs, therefore, the loss of one does not affect the availability, reliablility or other performance of the system

    ||read consistency levels|write consistency levels|
    |:---:|:---:|:---:|
    |1.|read one replica|commit to one replica|
    |2.|read quorum|commit to quorum|
    |3.|read all replicas|commit to all replicas|

    > $quorum = \left( \sum_{i=1}^n r_i / 2 \right) + 1$
    > where r is a replication factor

#### load balancing
* request traffic is directed to available nodes in such a way that a single not is not overwhelmed by requests
#### fault torelance
* idea is to have the system working even when an instance of a component fails
#### scalability
* idea is to spin or take down instances of services and/or DBs as the load increases or decreases respectively
### security
#### data-at-rest
* encrypt the data prior to storing it and/or encrypt the storage device itself
* use SHA, RSA etc
#### data-in-transit
* encrypt the data at multiple levels (assuming OSI model)
    * implement VPNs at network level
    * implement TLS at higher levels (session and presentation levels especially)
        - TLS, not SSL; the latter was deprecated in 2011
    * implement HTTPS at application level
#### access control
* define implement and enforce the roles + rights of a user (authorisation) and MFA to establish the identity of said user (authentication)
#### software vulnerabilities
* update software, libraries and OSs regularly
* apply the latest security patches to any 3<sup>rd</sup> party libraries, software etc
#### back-ups
* back up data regularly, preferably in an air-gapped DB
#### "common sense" security procedures
* use unique, uncommon passwords; passphrases are best
    - example: *Crunchy creamy Cookie candy Cupcake* . long, easy to remember, difficult to decrypt
### monitoring data integrity
* idea is to protect business data from known and/or unknown threats
* check if any changes have been made to vulnerable data
* assess the files of the DBs and file systems and generate a cryptographic check-sum as a baseline
    - re-calculate said check-sums regularly and compare with the baseline
    - if re-calculated &ne; baseline: *wagwaan, Frankie; we 'ave a problem*
    - this method allows us to detect hard-to-find threats e.g.  malware w/i OSs
    - this process can be resource-intensive; use on files and/or data that are more vulnerable to cyber attacks so that the resources freed can be invested efficiently
    - vulnerable data/files: user credentials, privileges, identities, encryption key stores, OS files, config files, app files etc

[def]: https://developer.safaricom.co.ke/
[def2]: https://github.com/brk-a/LearnWebAppPentesting/blob/main/0x0B-learn_pentesting/0x00-api_sec_fundamentals/0-real_world_api_breaches.md#what-the-researcher-did-3