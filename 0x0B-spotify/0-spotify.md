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

    ```mermaid
    ---
    title: spotify high-level
    ---
        flowchart LR
        A((user))-->B[load balancer]
        B-->C[spotify web server]
        C-->D[(DB)]
    ```

