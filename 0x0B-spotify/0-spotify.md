# 0x0B-spotify
* emphasis on finding and playing music
     - user can browse through a list of suggestions if they are new
     - user can browse through a list of favourites
     - user can search for a specific song
     - the app actually get the song to the user's ears
### high-level metrics
* 1 billions users
* 100 million songs
* typical `.mp3` audio is &approx; 5 MB; 100 million songs * 5 MB / song = 500 TB = 0.5 PB
    - assume 3x replication; raw audio requires *c.* 1.5 PB of space
* metadata, typically, is *c.* 100 B; 100 million songs * 100 B / song = 10 GB
    - metadata requires *c.* 10 GB of space
* user data may be, say, 1 KB large; 1 billion users * 1 KB / user = 1 TB
    - user data requires *c* 1 TB of space
* metrics on traffic coming soon ::hourglass::
### high-level layout
* user uses the mobile app to access spotify's nearest web server
* there is a load balance between the user and web server, of course
    - we may even implement a gateway
* spotify's web server talks to a DB
     - a read-and-write-heavy system
     - we have at least three types of data: raw audio, audio metadata and user data
     - perhaps a DB for each... 

    ```mermaid
    ---
    title: spotify high-level
    ---
        flowchart LR
        A((user))-->B[load balancer]
        B-->C[spotify web server]
        C-->D[(raw audio)]
        C-->E[(metadata: songs, artists, genres ... )]
        C-->F[(user data)]
    ```

* why multiple DBs?
    1. data types/formats are different
        - raw audio, for example, is an immutable blob (you will, almost certainly, never need to modify the file); the raw audio DB is read-heavy (Amazon S3 lends itself well)
        - metadata may or may not be immutable (Amazon RDS lends itself well)

            ```mermaid
            ---
            title: audio metadata object
            ---
                classDiagram
                class Song{
                    +String songID
                    +String songURL
                    +String artist
                    +String genre
                    +String albumCoverURL
                    +String audioLink
                }
            ```

        - user data is mutable (user changes their username/password etc). Also, this data is subject to various regulations (DPA, GDPR etc); you want to keep it seperate (Amazon RDS lends itself well)
    2. space requirements are different
        - recall 0.5 PB for raw audio etc
    3. read and write ferequency: the raw audio DB is, almost certainly, read-heavy;  the rest are, more or less, read-and-write-heavy
