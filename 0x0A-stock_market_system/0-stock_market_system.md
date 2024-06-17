# 0x0A-stock_market_system
* build a system that allows a user to buy and sell shares, derivatives, currency and other financial instruments online


    ```mermaid
    ---
    title: stock market system big picture
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
        Q-->S[()]
        Q-->T[kafka/SNS]
        subgraph other-services
        U[analytics service]
        V[notifications service]
        W[ticker]
        X[etc]
        end
        Q-->other-services
    ```