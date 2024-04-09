# sys arch and design for tinder
### features
1. storing profiles
    - PII
    - images (say, five per user)
2. recommending matches
    - MAUs
    - 
3. noting matches
    - probability of a match (per user)
    - 
4. DMs
### storing images
* file or blob?
    - blob &rarr; binary large object
* db has the following features: mutability, transaction guarantees, indexes and access control; plan accordingly
    - mutability: will you change the image? you could, but why do that when you can, simply, create a new row in the db? this is a feature we do not need
    - transaction guarantee: there is no need to enforce atomicity of a transaction w.r.t. images. this is a feature we do not need
    - indexes: are great for searche, sorting etc; this is a feature we do not need
    - access control: files are cheaper and faster than blobs. also, files are static, therefore, one can build a CDN over them
* db will store all the data, of course, however, it requires reference to the image file

    ```mermaid
    erDiagram
        USER ||--|| PROFILE : has
        PROFILE {
            string Id
            string userID
            string[] imageID
            string[] imageURL
        }
        USER{
            string Id
            string name
            string email
            string hashedPassword
        }
        PROFILE ||--|{ IMAGE : has
        IMAGE {
            string Id
            string profileID
        }
    ```

* profile service: sign up

    ```mermaid
        flowchart LR
        A[user]--username&token-->B[profile service]
        B--store-->C[(DB)]
        B-.may use.->D[email service]
    ```

* profile service: upload images (monolithic)

    ```mermaid
        flowchart LR
        A[user]--1 username&token-->B[profile service]
        A--2 upload images-->B
        B--3a store-->C[(DB)]
        B-.3b may use.->D[email service]
        B--4 response-->A
    ```

* profile service: upload images (microservice)

    ```mermaid
        flowchart LR
        A[user]--1 username&token-->B[gateway service]
        B--2 authenticated?-->C[profile service]
        C--3 Y/N-->B
        B--3a Yes, direct to upload service-->D[image service]
        D--4 store-->E[(DB)]
        B-.3b No, drop.->F[dropped]
        B--5 response-->A
        B-.->G[(DB)]
        D-.->H[DFS]
    ```

### DMs
* client A wants to talk to client B
    1. A tells gateway that it wants to talk to B using XMPP
        - username & token (auth)
        - A's id (id from)
        - B's id (id to)
        - message (payload)
    2. gateway uses XMPP to push message to B
* A, gateway and B connect using web-socket, TCP etc
    - gateway may maintain sessions (connection IDs, etc), however, this is inefficient
    - use a sessions service instead

    ```mermaid
        flowchart LR
        A[user A]--1 auth, idFrom, idTo, payload-->B[gateway service]
        B--2 authenticated?-->C[profile service]
        C--3 Y/N-->B
        B-.->D[image service]
        D-->E[(DB)]
        B--7 response-->A
        B-.->G[(DB)]
        D-.->H[DFS]
        B--3a Yes-->I[sessions service]
        B-.3b No, drop.->J[dropped]
        I--4 idTo? session? etc-->K[(DB)]
        K--4a alright, send payload-->I
        K-.4b No, drop.->L[dropped]
        I--5 alright, send payload-->B
        B--6 payload-->M[user B]
        C-.->N[(DB)]
    ```

### noting matches
* matching algo
    - may be dinic's or edmond-karp's algo
* matches will be stored on a server, not the client
    - server is the single source of truth
    - client can get data back if app is re-installed on a device or installed in a new device
* client talks to gateway service. gateway service talks to matcher service. matcher service is connected to a db that has a table containing `userID` (user's/client's id) and `userID` (match); one-to-many r/ship
* matcher service must talk to sessions service to find out if client is authorised to *talk to* (DM or otherwise contact) the match

     ```mermaid
        flowchart LR
        A[user]--1 auth, idFrom, idMatch-->B[gateway service]
        B--2 authenticated?-->C[profile service]
        C--3 Y/N-->B
        B-.->D[image service]
        D-.->E[(DB)]
        B--7 response-->A
        B-.->G[(DB)]
        D-.->H[DFS]
        B--3a Yes-->I[matcher service]
        B-.3b No, drop.->J[dropped]
        I--4 idMatch? session? etc-->K[sessions service]
        K--4a alright, talk to match-->I
        K-.4b No, drop.->L[dropped]
        I--5 alright, talk to match-->B
        B--6 talk to match-->M[match]
        C-.->N[(DB)]
        K-.->O[(DB)]
    ```

### recommending matches
* recommendation engine
    - how do we find out who is around where the user is?