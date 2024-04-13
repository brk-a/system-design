# sys design and arch for whatsapp
* microservice approach
### what to look at
* one-to-one chat
* group messaging
* sent, delivered and read receipts
* *online* and *last seen*
* sharing images &rarr; see [sys design for tinder][def]
* disappearing messages
### one-to-one messaging & sent+delivered+read receipts
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
    Message : +String Id
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
    title: user object
    ---
    classDiagram
    User : +String Id
    User : +String email
    User : +String phoneNumber
    User : +String location
    User : +Object profileImage
    User : +String[] groupsInID
    User : +sendMessage()
    User : +deactivateAccount()
    ```

    ```mermaid
    ---
    title: example flow
    ---
    flowchart LR
        L((users))--A & C & E
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

### *online* and *last seen*
* say B wants to know is A is online and, if not, when A was last online
    - there has to be a table that the B's gateway has access to
    - said db had A's id and the last time A was online
    - db is updated when A does anothing on the app (as long as A is connected to the internet)
    - there are two states: *online* and *last seen*; set the threshold at your discretion
    - example: db updates every 10 seconds, therefore, any timestamp under 10s means *online*
    - A's gateway must talk to a *last-seen* service. said gateway talks to the *last-seen* service any time A talks to the gateway. the service stores A's id and the timestamp of last comms with the gateway. said service must be smart enough to distinguish user-generated from system-generated activity

### group messaging
* say there are % users: A, B, C, D and E
* A, B and E are members of group 1; C, D and E are members of group 2
* idea is to have a message sent by a member of group 1 received by members of group 1 and no one else; same for group 2
* gateway does nothing except accept requests from users and pass on said request to parser/unparser service
* parser/unparser service, well, *parses* the electronic signal and converts it into a data structure/object
* sessions service does the following:
    - uses the auth service to, well, authenticate the user
    - creates a session for user
    - uses the group messaging service to find the group requested, make sure that the user is a member of said group and find the rest of the members of said group
        * use [consistent hashing][def2] to achieve the last one
    - uses the messaging service to send the message
* messaging service has a message queue. said queue allows messaes to be re-sent if, for one reason or another, the message is not sent on the first try
    - set the frequency of retries and time-to-message-destruction/expiration at your discretion
* success or failure responses are propagated to the sender at each stage 

    ```mermaid
    ---
    title: whatsapp group chat
    ---
    flowchart LR
    A((start))--B & C & D & E
    subgraph group_1
    B[user A]--1 auth, payload-->G[gateway service 1]
    C[user B]-->G
    F[user E]-->H
    end
    subgraph group_2
    D[user C]-->G
    E[user D]-->H[gateway service N]
    F-->H
    end
    G--2 forwards to-->Q[parser/unparser service]
    H-->Q
    Q--3 parses payload-->I[sessions service]
    I--5 verify group info-->J[group messaging service]
    I--4 auth-->K[auth service]
    I--6 message, group members IDs-->R[message service]
    G-.->L[(DB)]
    H-.->M[(DB)]
    I-.->N[(DB)]
    J-.->O[(DB)]
    K-.->P[(DB)]
    R-.->S[(DB)]
    R--7 message-->Q
    Q--8 parsed msg-->G
    Q--8 parsed msg-->H
    G--9 deliver-->C
    H--9 deliver-->E
    ```


[def]: ../0x01-tinder/0-tinder.md
[def2]: https://en.wikipedia.org/wiki/Consistent_hashing