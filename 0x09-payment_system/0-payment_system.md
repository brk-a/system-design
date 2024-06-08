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
    payment system components
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

[def]: https://developer.safaricom.co.ke/