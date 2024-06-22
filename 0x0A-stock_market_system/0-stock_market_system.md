# 0x0A-stock_market_system
* build a system that allows a user to buy and sell shares, derivatives, currency and other financial instruments online

### requirements
#### functional
* `sell` and `buy` features (core)
* users can specify a price for buying/selling stocks
* orders are served as limit orders
* orders not served are valid until market's CoB
* 10h active market time
* partial order matching feature
#### non-functional
* available
* consistent
* has trade fairness
* scale
    - orders ps: 60k (buy and sell)
    - stocks: 1000
#### out of scope
* update price candlestick charts
* list/delist stocks
#### capacity estimations
##### DB schema

    ```mermaid
    ---
    title: DB schema
    ---
        classDiagram
        class OrderRequest{
            +String orderID PK
            +String customerID
            +String stockID
            +int quantity
            +int perUnitPrice
            +String orderType
            +String status
        }
        class MatchedOrders{
            +String matchID PK
            +String buyOrderID
            +String sellOrderID
            +int quantity
            +int salePrice
        }
        class StockDetails{
            +String stockID PK
            +Object metadata
        }
    ```

##### APIs
* `buy(customerID, stockID, quantity, salePrice)`
* `sell(customerID, stockID, quantity, salePrice)`
* `matchOrders(buyOrderID, sellOrderID, quantity)`
* `getOrderStatus(orderID)`
##### storage estimates
* order requests
    * 100B/transaction * 60000 transactions/s * 86400 s/day * 365 days pa &approx; 100TB pa
    * &approx; 500TB in five years
* stock details
    * 100B/stock * 1000 stocks = 1 lakh B

### high level
* two interfaces: client-facing and stock-admin-portal-facing

    ```mermaid
    ---
    title: stock exchange system high level
    ---
        flowchart LR
        A[client]-->|buy or sell request| B[stock exchange service]
        B~~~C[stock admin portal]
        C-->|list or de-list stock| B
    ```

### high level w. a little more detail
* TLDR; the order request DB is read-and-write-heavy. it does not require asset properties transaction guarantees. it must be easy to scale, therefore, a NoSQL DB is best placed for the job
* order requests are in the hundreds of TBs
    - we need a DB that supports sharding/partitioning inherently
    - a NoSQL DB may be a great choice if we do not require asset properties transaction guarantees
    - the order requests DB simply stores orders; no financial transactions, therefore, no asset properties transaction guarantees are required
    - conclusion: said DB can be a NoSQL DB
* the NSE service stores orders in said NoSQL DB and the `status` property on the `order` object is set to *in progress*
    - said DB is dependent on the `buy` and `sell` APIs
    - users check the status of their orders by indirectly querying the DB
    - said order-status-seeking requests are checking the `orderID`, therefore, the order request DB can be partitioned by `orderID` which happens to be PK of the DB
* writes to the DB are buy and/or sell orders; reads to the DB are order status requests


    ```mermaid
    ---
    title: stock market system high level w. a little more detail
    ---
        flowchart LR
        A((client))-->B[load balancer]
        B-->C[NSE service]
        C-->D{sell or buy?}
        C-->E[(order request)]
        subgraph buy-queues
        F[EQTY]
        G[SCOM]
        H[CTUM]
        I[KEGN]
        J[etc]
        end
        subgraph sell-queues
        K[KCB]
        L[KPLC]
        M[BAT]
        N[etc]
        end
        D-->|buy| buy-queues
        D-->|sell| sell-queues
        buy-queues --> O[matcher service]
        O-->P[queue]
        P-->Q[executor service]
        Q-->R[deduct money service]
        Q-->S[(DB)]
        Q-->T[kafka/SNS]
        subgraph other-services
        U[analytics service]
        V[notifications service]
        W[ticker]
        X[etc]
        end
        Q-->other-services
    ```

### matching service
* clearly cannot be done synchronously
    - enter two queues: `buy` and `sell`
    - `buy` handles, well, buy orders; `sell` handles... you already know
* NSE service validates and places `buy` and sell orders in the respective queues
    - there is a queue for each stock in both the `buy` and `sell` queues
    - the NSE, as at Wed, 19 Jun, 2024 has 61 stocks listed; that means 124 queues total
        * two main queues: buy and sell
        * 61 queues under `buy`
        * 61 queues under `sell`
* matcher service polls both queues
    - idea is to match, say, $EQTY `sell` orders with $EQTY `buy` orders
    - matcher polls $EQTY `sell` and $EQTY `buy` order queues then matches `buy` and `sell` orders
    - Amazon SQS may help the matcher service consume messages from the queues; a message, once polled, cannot be seen by other consumers
    - we require at least two matcher nodes for each stock per main queue for reliablility and availability reasons
    - matcher service matches `buy` and `sell` prices
        * matches *buy* price X to *sell* price X &plusmn; *y* where *y* is a small, allowable price spread
            * example: match *buy* price 100 to *sell* price 100 &plusmn; 1.5 (98.5 to 101.5)
        * matches *sell* price X to *buy* price X or more
            * example: match *buy* price 100 to *sell* price 100 or more
    - if there are matches, handle matches, else, push messages back to respective queues; repeat process until CoB
    - orders that do not find a prospective match by CoB will be marked *expired*; they are stale, therefore, are dropped
    - in other words, the queues are empty at the beginning of each trading/business day
* how will partial matches be handled?
    - say there is a `buy` order for 100 units of $EQTY and a `sell` order for 120 units of $EQTY and that the price spreads match. clearly, the `sell` order can fulfill the `buy` one
    - what happens to the 20 units left over?
    - eea...sy! create a new `sell` order object containing 20 units and place it on the queue
    - conversely, create a `buy` order object containing 20 units and place it on the queue when the `buy` order is greater than the `sell` order by 20 units
### executor service
* `sell` and `buy` orders have been matched in whole or in part; what now?
* matched orders are place in a queue to be consumed by the executor service
* execution is a distributed transaction ( a database transaction where two or more network hosts are involved. usually, hosts provide transactional resources while a transaction manager creates and manages a global transaction that encompasses all operations against such resources)
* 

