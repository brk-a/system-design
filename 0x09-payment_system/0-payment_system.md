# payment system
* create a system that allows a buyer to pay for goods/services on an eCommerce website
### the problem
### requirements
* reliability
* correctness
* availability
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
        A((Customer))--places and order-->B[merchant website]
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
