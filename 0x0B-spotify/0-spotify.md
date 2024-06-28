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
        C-->E[(metadata:<br/>songs,<br/>artists,<br/>genres<br/>... )]
        C-->F[(user data)]
    ```

* why multiple DBs?
    1. data types/formats are different
        - raw audio, for example, is an immutable blob (you will, almost certainly, never need to modify the file); the raw audio DB is read-heavy (Amazon S3 lends itself well)
        - metadata may or may not be immutable (Amazon RDS lends itself well); also this DB needs to be relational

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
### finding music
* user may type in the song's name, artist or genre; we need to return the result that matches the song search query closest
* user data is sent as a `GET` request to the spotify web service
    * the request is  translated to a query that the metadata DB understands
    * DB returns the metadata of the search results to the UI
    * notice how we do not touch the raw audio DB
* user clicks on the song they want to listen to
    * the click becomes a request from the user to the spotify web server
    * the the request is translated to a query metadata DB understands
    * metadata DB returns the `audioLinks` property to the web server
    * we can, finally, query the raw audio DB: the web server  queries the raw audio DB
    * raw audio DB returns the audio to the spotify web server which, in turn, returns it to the user
        - we could return the audio chunk by chunk; a web socket is required to achieve this
        - a more efficient method: return the whole audio file (it is 5 MB, after all; the web server can take that); no web sockets or such other expensive operations
        - the second method eliminates the lag between the DB and web server (the streaming does not begin until the audio file is in the web server)
### bottlenecks
##### most played/viral songs
* TL:DR: the songs most listened to can be fetched from a cache instead of the DB. we use a CDN to achieve this. said CDN is told by the web server what songs to fetch from the DB. AWS CloudFront or equivalent works
* pareto principle: majority of effects come from minority of causes
    - in this case, majority of calls to raw audio DB are for a minority of the songs
    - let the minority proportion be, say, 10% (i.e. 10 million songs)
    - newly released hit/viral songs are included in the 20%
    - let the majority proportion be, say, 50% (i.e. 500 million users)
* we have half a billion requests to play 10 million songs (we could apply the principle recursively on this sample as many times as we want. think the 1% of the 1% of the 1% etc)
    - 250 million users request for two million  songs
    - 125 million users request for 400,000 songs
    - etc
* the requests
    - could overwhelm the DBs. also, the same song will be loaded to majority of the web servers
    * reach/exceed the bandwidth constraints
* enter the CDN (content delivery network)
    - it is a cache of sorts
    - it reduces the amount of load to the back end
    - typically close to the user from the perspective of number of hops/network connections
    - said CDN will cache/store the most commonly streamed audio files
    - of, course, it requires a direct connection to the DB to be able to update itself
    - said cache can be accessed by users instead of the DB
    - the data/metadata required to update the CDn will be on the web server

    ```mermaid
    ---
    title: spotify w. CDN high-level
    ---
        flowchart LR
        A((user))-->B[load balancer]
        B-->C[spotify web server]
        C-->D[(raw audio)]
        C-->E[(metadata:<br/>songs,<br/>artists,<br/>genres<br/>... )]
        C-->F[(user data)]
        C-->|updates| G[CDN]
        G-->|fetches from| D
        G-->|streams to| A
    ```

* user will be able to see the latest/most played/viral songs right after turning the app on (and connection to the internet, of course) because the web server will have already updated the CDN and said CDN will update the UI when the user opens the app
##### optimisation
TL;DR: implement multi-layer caching
* web servers could have their own cache too: a shared one or one that is local to each
    - this way, the song is loaded from the DB to the local/shared cache and uploaded to the CDN if necessary
* a user's own memory can be used to store, say, 15 of the songs said user plays the most
##### load balancing
* 
