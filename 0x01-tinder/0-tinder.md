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
        B-->D[image service]
        D-->E[(DB)]
        B--7 response-->A
        B-.->G[(DB)]
        D-.->H[DFS]
        B--3a Yes-->I[sessions service]
        B-.3b No, drop.->J[drop]
        J-.->K[dropped]
        I--4 idTo? session? etc-->L[(DB)]
        L--4a alright, send payload-->I
        L-.4b No, drop.->M[dropped]
        I--5 alright, send payload-->B
        B--6 payload-->N[user B]
        C-.->O[(DB)]
    ```

### noting matches
* matching algo
### recommending matches