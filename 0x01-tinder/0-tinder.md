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

* profile service: upload images (monolithic)

    ```mermaid
        flowchart LR
        A[user]--1 username&token-->B[gateway service]
        B--2 authenticated?-->C[profile service]
        C--3a Yes/No-->B
        B--4 Yes, direct to upload service-->D[image service]
        D--5 store-->E[(DB)]
        B-.3b No, drop.->F[dropped]
        B--6 response-->A
        B-.->G[(DB)]
        D-.->H[DFS]
    ```
