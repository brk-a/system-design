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
    title: Db schema
    ---
        classDiagram
        class OrderRequest {
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
            +String stockID
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
    * 100B/transaction * 60000 transactions/s * 86400 s/day * 365 days pa = &approx; 100TB pa
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
        C-->|buy| buy-queues
        C-->|sell| sell-queues
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