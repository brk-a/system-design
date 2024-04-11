# sys design and arch for whatsapp
* microservice approach
### what to look at
* one-to-one chat
* group messaging
* sent, delivered and read receipts
* *online* and *last seen*
* sharing images &rarr; see [sys design for tinder][def]
* disappearing messages
### one-to-one messaging
* user A wants to send a message to user B
    * A talks to gateway
    * gateway talks to sessions service (auth, session, B's ID, message etc)
    * sessions service talks to DB
        - is user A really user A? (auth)
        - is the session valid?
        - where is B's gateway service located?
    * auth & session are alright: send message to B
    * auth and/or session are not alright: drop
* recall: gateway services are servers, therefore, they cannot *send* anything to clients
    * servers *serve*, that is, accept requests and return responses
    * you can use long polling, web sockets or server-sent events so user B can get the message from the gateway service
    * web sockets are best placed for this purpose
    * B's gateway caches the message until it is delivered to B

    ```mermaid
    ---
    title: message object
    ---
    classDiagram
    Message : +String fromID
    Message : +String toID
    Message : +String payload
    Message : +Boolean sent
    Message : +Boolean delivered
    Message : +Boolean read
    Message : +sendSentReceipt()
    Message : +sendDeliveredReceipt()
    Message : +sendReadReceipt()
    ```


    ```mermaid
    ---
    title: example flow
    ---
    graphLR
        A[user A]--1 auth, message-->B[gateway service 1]
        C[user B]-->D[gateway service 2]
        E[user X]-->F[gateway service N]
        B--2 auth, message-->G[sessions service]
        D-->G[sessions service]
        F-->G[sessions service]
        G--3 auth? session?-->H[(DB)]
        H--4a in order, proceed-->G
        H-.4b not in order, drop.->I[dropped]
        G--5 toId's gateway?-->J[(DB)]
        J--6 here it is-->G
        G--7 toID, message-->D
        D--8 stores message in-->K[(DB)]
        D--9 message-->C
        G--10a response: sent receipt-->B
        B--10b response: sent receipt-->A
        C--11a response: delivered receipt-->D
        D--11b response: delivered receipt-->G
        G-.11c response: delivered receipt.->J
        J-.11d response: delivered receipt.->G
        G--11e response: delivered receipt-->B
        B--11f response: delivered receipt-->A
        C--12a response: read receipt-->D
        D--12b response: read receipt-->G
        G-.12c response: read receipt.->J
        J-.12d response: read receipt.->G
        G--12e response: read receipt-->B
        B--12f response: read receipt-->A
    ```

* 

[def]: ../0x01-tinder/0-tinder.md